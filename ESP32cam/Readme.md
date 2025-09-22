# MONO_ROBOT – ESP32-CAM to Raspberry Pi (TCP Streaming)

This project demonstrates how to stream **camera frames from an ESP32-CAM (XIAO ESP32S3 + OV2640)** to a **Raspberry Pi** over **TCP sockets** when both devices are connected to the same network.  

The ESP32 captures JPEG frames and sends them to the Pi, which saves them as image files for further processing (e.g., computer vision, robotics, AI).  

---

## 📸 System Overview


- **ESP32-CAM**: Captures frames and transmits them over TCP.  
- **Raspberry Pi**: Runs a Python server, receives frames, decodes JPEG data, and saves them to disk.  

---

## 🚀 Features
- Stream JPEG frames from ESP32-CAM over Wi-Fi.  
- TCP-based communication for reliability.  
- Raspberry Pi automatically saves incoming frames.  
- Tested on **ESP32-S3 with PSRAM** and **Raspberry Pi 4**.  

---

## 🛠 Requirements

### Hardware
- ESP32-CAM (XIAO ESP32S3 or similar with OV2640 camera)  
- Raspberry Pi (or any Linux server with Python3 + OpenCV installed)  
- Wi-Fi network (both devices must be connected to the **same network**)  

### Software
- Arduino IDE (for ESP32-CAM code upload)  
- Python 3.8+ on Raspberry Pi  
- Python packages: `opencv-python`, `numpy`  

Install dependencies on Pi:  
```bash
sudo apt update && sudo apt install python3-opencv python3-numpy -y
