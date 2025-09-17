import socket
import time
import math
import json
import threading
import queue
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

# ====== UDP設定 ======
PC_IP = "0.0.0.0"
UNITY_PORT = 7001

# ====== myCobot送信設定 ======
MYCOBOT_IP = "172.22.94.105"   # ← myCobot Raspberry Pi のIP
MYCOBOT_PORT = 7010

# ====== stretchSense受信設定 ======
GLOVE_PORT = 9400

# ====== キュー（スレッド間共有） ======
angle_queue = queue.Queue()
gripper_queue = queue.Queue()

# ====== mocopi受信 ======
def get_mocopi_data():
    """Unityからmocopiデータを受け取ってanglesを計算し、キューに格納"""
    sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_in.bind((PC_IP, UNITY_PORT))
    print(f"[Bridge] Listening Unity vector on {PC_IP}:{UNITY_PORT}")

    while True:
        
        data, _ = sock_in.recvfrom(1024)
        msg = data.decode("utf-8").strip()
        try:
            vx, vy, vz = [float(v) for v in msg.split(",")]

            # ====== ベクトルから角度算出 ======
            yaw = math.degrees(math.atan2(vx, vz))   # J1
            pitch = math.degrees(math.asin(vy))      # J2
            elbow = 0                                # J3仮置き
            roll = 0                                 # J6仮置き

            # ====== マッピング ======
            j1 = -max(min(yaw, 60), -60)
            j2 = -max(min(pitch, 45), -45)  # 上下反転補正
            j3 = elbow
            j6 = roll

            angles = [90 + j1, 90 + j2, j3, -90, -90, 90 + j6]

            # キューに格納
            angle_queue.put(angles)

        except Exception as e:
            print("parse error (mocopi):", e)

# ====== stretchSense受信 ======
#=======================================================================
#=======================================================================
#=======================================================================

latest_clean = None

def slider_handler(addr, *args):
    global latest_clean
    # print("OSC recv:", addr, args)  # デバッグ出力
    sensor_values = args[5:]
    clean = [v for v in sensor_values if v != -2147483648]
    if len(clean) == 12:
        latest_clean = clean

def to_10scale(x):
    return round(x * 10, 1)

async def handle_glove(loop, gripper_queue, PC_IP, GLOVE_PORT):
    global latest_clean

    dispatcher = Dispatcher()
    dispatcher.map("/v1/animation/slider/all", slider_handler)

    server = AsyncIOOSCUDPServer((PC_IP, GLOVE_PORT), dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()

    try:
        while True:
            await asyncio.sleep(0.01)  # ★必ずsleepを入れてイベントループを回す
            if latest_clean is not None:
                clean = latest_clean
                index_base  = clean[4]
                middle_base = clean[6]
                ring_base   = clean[8]
                pinky_base  = clean[10]
                thumb_base  = clean[0]

                avg_small_ring = (pinky_base + ring_base) / 2
                avg_mid_index  = (middle_base + index_base) / 2
                combined_mean  = (avg_small_ring + avg_mid_index) / 2

                data = [
                    to_10scale(avg_small_ring) * 10,
                    to_10scale(avg_mid_index) * 10,
                    to_10scale(thumb_base) * 10
                ]
                print("send_data:", data)
                gripper_queue.put(data)

                latest_clean = None
    finally:
        transport.close()

def get_stretch_sense_data(gripper_queue, PC_IP, GLOVE_PORT):
    """スレッドから呼び出す関数"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        print("start")
        loop.run_until_complete(handle_glove(loop, gripper_queue, PC_IP, GLOVE_PORT))
    finally:
        loop.close()

# ====== メイン制御 ======
def main():
    """最新のanglesとgripperデータをキューから取り出してmyCobotに送信"""
    sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Bridge: Sending to myCobot...")

    last_print_time = time.time()
    latest_angles = None
    latest_gripper = None

    while True:
        try:
            # 最新のanglesだけ取得
            while not angle_queue.empty():
                latest_angles = angle_queue.get_nowait()

            # 最新のgripperだけ取得
            while not gripper_queue.empty():
                latest_gripper = gripper_queue.get_nowait()

            if latest_angles is None and latest_gripper is None:
                time.sleep(0.01)
                continue

            # ====== 送信用データを構築 ======
            payload = {}
            if latest_angles is not None:
                payload["angles"] = latest_angles
            if latest_gripper is not None:
                payload["gripper"] = latest_gripper

            # JSONで送信
            packet = json.dumps(payload).encode("utf-8")
            sock_out.sendto(packet, (MYCOBOT_IP, MYCOBOT_PORT))

            # 0.5秒ごとにログ出力
            now = time.time()
            if now - last_print_time >= 0.5:
                print("[Bridge] send:", payload)
                last_print_time = now

        except Exception as e:
            print("control error:", e)

if __name__ == "__main__":
    # mocopiスレッド
    t1 = threading.Thread(target=get_mocopi_data, daemon=True)
    t1.start()

    # stretchSenseスレッド（引数を渡す！）
    t2 = threading.Thread(
        target=get_stretch_sense_data,
        args=(gripper_queue, PC_IP, GLOVE_PORT),
        daemon=True
    )
    t2.start()

    # メイン制御ループ
    main()
