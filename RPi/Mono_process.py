"""
Monocular Visual Odometry with ESP32-CAM + Raspberry Pi
--------------------------------------------------------

This script:
1. Receives frames sent by an ESP32-CAM using the tcp_server module.
2. Runs a monocular visual odometry (VO) pipeline to estimate relative
   camera motion between frames using optical flow and the essential matrix.

Author: Harsha Vardhan Reddy Yerranagu
Repo: https://github.com/Harshavardhan200/MONO_ROBOT
"""

import cv2
import numpy as np
import rpi_frame_storage as tcp


class MonoVO:
    def __init__(self, fc, pp: tuple, k: np.array):
        self.fc = fc
        self.pp = pp
        self.k = k

    def featureTracking(self, image_1, image_2, points_1):
        """Track features between two frames using Lucas-Kanade optical flow."""
        lk_params = dict(winSize=(21, 21),
                         maxLevel=3,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

        if len(points_1) == 0:
            print("⚠️ No points to track in the first frame!")
            return None, None

        points_1 = points_1.reshape(-1, 1, 2)
        points_2, status, _ = cv2.calcOpticalFlowPyrLK(image_1, image_2, points_1, None, **lk_params)

        if points_2 is None or status is None:
            print("⚠️ Failed to track points between frames!")
            return None, None

        status = status.reshape(status.shape[0])
        points_1 = points_1[status == 1]
        points_2 = points_2[status == 1]

        return points_1, points_2

    def monoVO(self, frame_0, frame_1):
        """Run monocular VO between two frames."""
        if frame_0 is None or frame_1 is None:
            print("❌ Invalid frames received!")
            return None, None

        # Detect FAST features
        detector = cv2.FastFeatureDetector_create()
        kp1 = detector.detect(frame_0)
        points_1 = np.array([ele.pt for ele in kp1], dtype='float32')

        if len(points_1) == 0:
            print("⚠️ No keypoints detected in the first frame!")
            return None, None

        # Track features
        points_1, points_2 = self.featureTracking(frame_0, frame_1, points_1)
        if points_1 is None or points_2 is None:
            print("❌ Feature tracking failed!")
            return None, None

        # Estimate Essential Matrix and Recover Pose
        E, _ = cv2.findEssentialMat(points_2, points_1, self.fc, self.pp, cv2.RANSAC, 0.999, 1.0)
        _, R, T, _ = cv2.recoverPose(E, points_2, points_1, focal=self.fc, pp=self.pp)

        return R, T


def run_monocular_vo(frames):
    """Run VO on a list of frames."""
    fc = 476.7030836014194
    pp = (400.5, 400.5)
    k = np.array([[fc, 0, pp[0]], [0, fc, pp[1]], [0, 0, 1]])
    mono = MonoVO(fc, pp, k)

    car_pos = np.zeros(3)
    car_rot = np.eye(3)

    for i in range(len(frames) - 1):
        frame_1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        frame_2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)

        R, T = mono.monoVO(frame_1, frame_2)
        if R is None or T is None:
            continue

        delta = np.dot(car_rot, T).flatten()
        car_pos += delta
        car_rot = np.dot(car_rot, R)

        print(f"📍 Updated Position: {car_pos}")
        print(f"🌀 Updated Rotation:\n{car_rot}")


if __name__ == "__main__":
    # First test with locally saved frames (frames/frame_1.jpg, frame_2.jpg, ...)
    frames = []
    for i in range(1, 3):  # load first 2 frames
        frame = cv2.imread(f"frames/frame_{i}.jpg")
        if frame is not None:
            frames.append(frame)

    if len(frames) >= 2:
        print("▶️ Running VO on saved frames...")
        run_monocular_vo(frames)

    # Then wait for new frames from ESP32-CAM
    frames = []
    tcp.start_server(frames)
    if len(frames) >= 2:
        print("▶️ Running VO on received frames...")
        run_monocular_vo(frames)
    else:
        print("⚠️ Not enough frames received for VO!")
