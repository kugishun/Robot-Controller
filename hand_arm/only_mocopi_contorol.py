import socket
import json
import threading
import queue
import time
from pymycobot.mycobot import MyCobot
# from MyHand import MyGripper_H100

# ====== UDP受信設定 ======
IP = "0.0.0.0"
PORT = 7010

# ====== キュー（受信データを処理スレッドに渡す） ======
data_queue = queue.Queue()

# ====== myCobot制御周期 ======
CONTROL_HZ = 20
CONTROL_INTERVAL = 1.0 / CONTROL_HZ
LOG_INTERVAL = 0.5

def udp_receiver():
    """UDPでデータを受信してキューに格納"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print(f"[myCobot Server] Listening on {IP}:{PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            msg = json.loads(data.decode("utf-8"))
            data_queue.put(msg)   # キューに追加
        except Exception as e:
            print("UDP recv error:", e)

def data_processor():
    """常に最新のデータだけを20Hz上限で処理"""
    mc = MyCobot("/dev/ttyAMA0", 115200)
    # hand = MyGripper_H100("/dev/ttyCH343USB0")
    mc.power_on()
    # hand.set_gripper_pose(4, 15)
    mc.set_fresh_mode(1)

    latest_msg = None
    next_control_time = time.monotonic()
    last_log_time = 0.0

    while True:
        try:
            # キューを一気に掃き出し、最新の1件だけ保持する
            while not data_queue.empty():
                latest_msg = data_queue.get_nowait()

            now = time.monotonic()
            if latest_msg is None:
                time.sleep(0.001)  # CPU負荷軽減
                continue

            if now < next_control_time:
                time.sleep(min(0.001, next_control_time - now))
                continue

            msg_to_send = latest_msg
            latest_msg = None
            next_control_time = now + CONTROL_INTERVAL

            if "angles" in msg_to_send:
                angles = msg_to_send["angles"]
                if now - last_log_time >= LOG_INTERVAL:
                    print("[Processor] angles:", angles)
                    last_log_time = now
                mc.send_angles(angles, 50)

            if "gripper" in msg_to_send:
                gripper = msg_to_send["gripper"]
                if now - last_log_time >= LOG_INTERVAL:
                    print("[Processor] gripper:", gripper)
                    last_log_time = now
                # hand.set_gripper_joint_angle(1, int(gripper[2]))
                # hand.set_gripper_joint_angle(2, int(gripper[1]))
                # hand.set_gripper_joint_angle(3, int(gripper[0]))

        except Exception as e:
            print("Process error:", e)

if __name__ == "__main__":
    # UDP受信スレッド
    t1 = threading.Thread(target=udp_receiver, daemon=True)
    t1.start()

    # 処理スレッド
    t2 = threading.Thread(target=data_processor, daemon=True)
    t2.start()

    # メイン待機
    while True:
        time.sleep(1)
