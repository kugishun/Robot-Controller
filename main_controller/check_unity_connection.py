import socket

# Unity側の送信先ポート番号と合わせる
IP = "0.0.0.0"    # すべてのNICで受信
PORT = 7001       # Unityの remotePort と一致

# UDPソケットを作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"[Test Receiver] Listening on {IP}:{PORT} ...")
print("Unityから送信されるデータを待機中...\n")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode("utf-8").strip()
        print(f"Received from {addr}: {msg}")
except KeyboardInterrupt:
    print("\n終了しました。")
except Exception as e:
    print("Error:", e)
finally:
    sock.close()
