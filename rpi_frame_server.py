"""
Raspberry Pi TCP Frame Receiver
--------------------------------
Receives JPEG frames sent from an ESP32-CAM over TCP,
decodes them, saves them to disk, and keeps them in memory.

Usage:
1. Run this script on Raspberry Pi.
2. ESP32-CAM should connect to Pi's IP and port defined here.
3. Frames will be saved into the 'frames' folder.

Author: Harsha Vardhan Reddy Yerranagu
Repo: https://github.com/Harshavardhan200/MONO_ROBOT
"""

import socket
import struct
import os
import cv2
import numpy as np
import time

# ==== Server Settings ====
HOST = "0.0.0.0"   # Listen on all interfaces
PORT = 8080
SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)


def recv_all(sock, size):
    """Receive exactly size bytes from the socket."""
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data


def start_server(frames):
    """Start the TCP server that receives frames from ESP32-CAM."""
    frame_count = 0
    start_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"📡 Server listening on {HOST}:{PORT}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"✅ Connected by {addr}")

            with client_socket:
                while True:
                    # Receive frame size
                    size_bytes = recv_all(client_socket, 4)
                    if not size_bytes:
                        print("⚠️ Client disconnected")
                        break

                    frame_size = struct.unpack("i", size_bytes)[0]

                    if frame_size == -1:
                        # ESP32 reported error
                        err_msg = client_socket.recv(1024).decode(errors="ignore")
                        print(f"❌ Frame capture failed: {err_msg}")
                        continue

                    # Receive frame data
                    frame_data = recv_all(client_socket, frame_size)
                    if not frame_data:
                        print("⚠️ Frame data not received, client disconnected")
                        break

                    # Decode JPEG -> OpenCV image
                    np_arr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                    # Save and store frame
                    frame_count += 1
                    frame_path = os.path.join(SAVE_DIR, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_path, frame)
                    frames.append(frame)
                    print(f"📸 Saved {frame_path}")

                    # Performance check (optional)
                    if frame_count >= 2:
                        end_time = time.time()
                        total_time = end_time - start_time
                        speed = frame_count / total_time
                        print(f"🕒 Total time: {total_time:.2f} seconds")
                        print(f"🚀 Transmission speed: {speed:.2f} FPS")
                        break
                break


if __name__ == "__main__":
    frames = []
    start_server(frames)
    print(f"✅ Done. Received {len(frames)} frames.")
