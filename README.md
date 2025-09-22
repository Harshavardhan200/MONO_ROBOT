# MONO_ROBOT

**MONO_ROBOT** is a project that implements **monocular vision** for a robot using a single camera (ESP32-CAM). The system enables the robot to perceive its environment, track motion, and estimate its position and orientation using computer vision techniques.

The repository is structured to separate the **ESP32-CAM capture**, **Raspberry Pi frame reception**, and **monocular visual odometry processing**.

---

## 📂 Repository Structure

MONO_ROBOT/
│
├── RPi/
│ ├── rpi_frame_storage/ # Folder where ESP32-CAM frames are saved
│ ├── rpi_frame_server.py # TCP server to receive frames from ESP32-CAM
│ └── mono_process.py # Monocular Visual Odometry (VO) processing
│
├── ESP32_CAM/
│ └── esp32_tcp_client.ino # ESP32-CAM code to capture and send frames over TCP
│
├── README.md



---

## 🔹 Folder Details

### 1️⃣ `ESP32_CAM/`
- Contains the code for **ESP32-CAM** to:
  - Capture images using the OV2640 camera.
  - Connect to the Raspberry Pi via TCP over Wi-Fi.
  - Send images continuously to the Pi for storage and processing.
- Acts as the **robot’s eye** in the system.

### 2️⃣ `RPi/rpi_frame_storage/`
- Destination folder where the Raspberry Pi stores images received from ESP32-CAM.
- Each frame is saved as `frame_1.jpg`, `frame_2.jpg`, etc.
- These images are later used for **monocular VO processing**.

### 3️⃣ `RPi/rpi_frame_server.py`
- Runs a **TCP server** on the Raspberry Pi.
- Receives JPEG frames sent by ESP32-CAM.
- Saves each frame to `rpi_frame_storage/` and keeps them in memory.
- Provides frames to the VO module for processing.

### 4️⃣ `RPi/mono_process.py`
- Implements **monocular visual odometry**:
  - Detects and tracks features between consecutive frames using FAST detector and Lucas-Kanade optical flow.
  - Estimates the **essential matrix** and recovers **rotation (R)** and **translation (T)**.
  - Updates the robot's **3D position** and **orientation** in space.
- Uses frames stored in `rpi_frame_storage/` for processing.

---

## 🚀 Workflow

1. **ESP32-CAM captures images** using its camera module.
2. **ESP32-CAM sends frames** via TCP to the Raspberry Pi over Wi-Fi.
3. **Raspberry Pi receives frames** with `rpi_frame_server.py`:
   - Saves frames in `rpi_frame_storage/`.
   - Keeps frames in memory for immediate VO processing.
4. **Monocular VO processing** is executed by `mono_process.py`:
   - Computes robot motion between consecutive frames.
   - Updates the robot’s 3D **position** and **orientation**.
5. Optionally, the system can **visualize trajectory** or provide **real-time navigation cues**.

---

## 🔹 How Directions Are Determined

- The VO module tracks **keypoints** in consecutive frames.
- Computes the **essential matrix** between frames to understand **camera motion**.
- Extracts **rotation (R)** and **translation (T)** from the essential matrix.
- Updates the robot's **global position** using:
  ```python
  car_pos += car_rot @ T
  car_rot = car_rot @ R




