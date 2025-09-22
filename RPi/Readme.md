# MONO_ROBOT – ESP32-CAM to Raspberry Pi with Monocular Visual Odometry

This project demonstrates how to use an **ESP32-CAM** (XIAO ESP32S3 + OV2640) to stream camera frames over **TCP** to a **Raspberry Pi**, where the frames are received, saved, and processed using **Monocular Visual Odometry (VO)** with OpenCV.  

It combines two key parts:  

1. **TCP Frame Receiver (`tcp_server.py`)** – A Raspberry Pi TCP server that receives `.jpg` images from the ESP32-CAM and stores them locally.  
2. **Monocular VO (`mono_vo.py`)** – Python code that takes consecutive frames and estimates camera **position** and **orientation** using feature tracking and the Essential Matrix.  

---

## 📂 How It Works

### Network Communication
- Both ESP32-CAM and Raspberry Pi are connected to the **same Wi-Fi network**.  
- The Raspberry Pi runs a TCP server (`tcp_server.py`) listening on **port 8080**.  
- The ESP32-CAM connects to the Pi’s IP address and sends **JPEG frames** over TCP.  
- Each frame is received, decoded, and saved in `frames/frame_1.jpg`, `frames/frame_2.jpg`, etc.  

### Visual Odometry (VO)
- VO estimates the **motion of the camera** by comparing consecutive frames.  
- Steps involved:
  1. **Feature Detection** – Keypoints (corners/edges) are extracted from the first frame using **FAST feature detector**.  
  2. **Feature Tracking** – Keypoints are tracked in the second frame using **Lucas-Kanade Optical Flow**.  
  3. **Essential Matrix (E)** – Encodes relative motion between two camera views, computed from tracked feature points.  
  4. **Pose Recovery** – From `E`, we extract **Rotation (R)** and **Translation (T)**.  
     - `R` = How much the camera rotated  
     - `T` = The direction the camera moved (up, down, forward, left, right)  
  5. **Trajectory Update** – The car’s estimated **position (x, y, z)** and **orientation** are updated after each frame pair.  

---

## 📜 Files

### 1. `tcp_server.py`
Handles receiving frames from the ESP32-CAM.  

- **Starts TCP Server** on Raspberry Pi (`0.0.0.0:8080`).  
- Waits for ESP32-CAM to connect.  
- Receives image size first, then the JPEG image bytes.  
- Decodes the image with OpenCV.  
- Saves it as `frames/frame_N.jpg`.  

📌 *This script ensures the Pi continuously collects frames for VO.*  

---

### 2. `mono_vo.py`
Implements **Monocular Visual Odometry**.  

Key Components:
- **`featureTracking`** – Tracks features between two frames using Lucas-Kanade optical flow.  
- **`monoVO`** – Computes Essential Matrix and recovers `R` and `T`.  
- **`run_monocular_vo`** – Iterates over frames, updates car position (`car_pos`) and orientation (`car_rot`), and prints them.  

Example Output:

---

### 🔍 Breaking Down the Output

1. **Updated Position**  

- This is the estimated **cumulative translation vector** (x, y, z).  
- Interpreted as:
  - `x = -0.58` → movement to the **left**  
  - `y = -0.40` → slight movement **downwards**  
  - `z = +0.70` → movement **forward**  

2. **Updated Rotation (R)**  
- A **rotation matrix** that represents the camera’s new orientation.  
- Values close to **identity matrix** mean very little rotation (straight path).  
- Small off-diagonal values (`0.008`) indicate minor angular adjustments.  

3. **Direction of Movement**  

- A **unit direction vector** pointing in the movement direction.  
- Useful for trajectory plotting or navigation commands (e.g., “forward-left”).  

4. **TCP Server Logs**  
- Confirms that the Pi’s TCP server is running, the ESP32-CAM connected, and frames are being saved.  

5. **Performance Stats**  
- Measures **end-to-end frame transmission speed** from ESP32-CAM → Pi.  
- Can be optimized by lowering JPEG size or using a faster Wi-Fi link.  

---

## 📈 Interpreting Directions

From the above output:
- The car/robot is moving **forward-left** (negative X, positive Z).  
- It is also slightly **descending** (negative Y).  
- Rotation shows the robot is staying nearly aligned (minimal angular deviation).  

This demonstrates how VO can extract **real-world movement directions** purely from consecutive camera frames.

---

## 📡 Debugging & Tuning
- If `Updated Position` does not change → Not enough **features detected** (try adding texture to environment).  
- If `Transmission speed` is low → Reduce image resolution or optimize Wi-Fi quality.  
- If frames are blurry → Increase shutter speed or improve ESP32-CAM lighting.  

---

