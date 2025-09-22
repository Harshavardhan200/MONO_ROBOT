# Raspberry Pi – TCP Frame Receiver

This component of the **MONO_ROBOT** project runs a **TCP server** on the Raspberry Pi to receive and save camera frames sent from an **ESP32-CAM (XIAO ESP32S3 + OV2640)**.  

Frames are received over Wi-Fi (TCP), decoded, and stored as `.jpg` files inside the `frames/` directory.  

---

## 📂 How It Works
1. The Raspberry Pi runs `rpi_frame_server.py`, which listens on port **8080**.  
2. The ESP32-CAM connects to the Pi’s IP address and sends JPEG frames over TCP.  
3. Each received frame is:  
   - Decoded into an OpenCV image  
   - Saved in the `frames/` folder as `frame_1.jpg`, `frame_2.jpg`, …  
   - Kept in memory (for further CV/AI tasks if needed)  

---

## 🚀 Usage

### 1. Install Dependencies
Make sure Python3 and required libraries are installed on your Raspberry Pi:  
```bash
sudo apt update
sudo apt install python3-opencv python3-numpy -y
