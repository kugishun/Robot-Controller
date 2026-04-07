import socket
import json
import threading
import queue
import time
from pymycobot.mycobot import MyCobot
from MyHand import MyGripper_H100

# ====== UDP受信設定 ======
IP = "0.0.0.0"
PORT = 7010

# ====== キュー（受信データを処理スレッドに渡す） ======
data_queue = queue.Queue()

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
    """常に最新のデータだけ処理"""
    mc = MyCobot("/dev/ttyAMA0", 115200)
    hand = MyGripper_H100("/dev/ttyCH343USB0")
    mc.power_on()
    hand.set_gripper_pose(4, 15)

    while True:
        try:
            latest_msg = None
            # キューを一気に掃き出し → 最後の1件だけ残す
            while not data_queue.empty():
                latest_msg = data_queue.get_nowait()

            if latest_msg is None:
                time.sleep(0.001)  # CPU負荷軽減
                continue

            if "angles" in latest_msg:
                angles = latest_msg["angles"]
                print("[Processor] angles:", angles)
                mc.send_angles(angles, 30)

            if "gripper" in latest_msg:
                gripper = latest_msg["gripper"]
                print("[Processor] gripper:", gripper)
                hand.set_gripper_joint_angle(1, int(gripper[2]))
                hand.set_gripper_joint_angle(2, int(gripper[1]))
                hand.set_gripper_joint_angle(3, int(gripper[0]))

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
