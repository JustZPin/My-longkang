#!/usr/bin/env python3
"""Project 2 (Laptop side) — Flood-robot ground station entry point.

Wires the concerns together:
  camera.StreamReceiver  -> receive H.264 frames over UDP (GStreamer)
  overlay.sample_center_hsv / draw_overlay -> sample + annotate
  classifier.classify_waste -> map centre HSV to a drain-blockage material

Matches the robot stream: host 192.168.121.254, port 5002.
Requires OpenCV built WITH GStreamer support (see docs/setup.md).
Start the robot (flood_robot_pi.py) first.

Plain view-only equivalent (no classification):
  gst-launch-1.0 udpsrc port=5002 caps="application/x-rtp,media=video,\
encoding-name=H264,payload=96,clock-rate=90000" buffer-size=800000 \
! rtph264depay ! avdec_h264 ! videoflip method=2 ! autovideosink
"""
import cv2

try:
    # When run as a package: python -m ground_station.main
    from .camera import StreamReceiver
    from .classifier import classify_waste
    from .overlay import draw_overlay, sample_center_hsv
except ImportError:
    # When run as a script: python src/ground_station/main.py
    from camera import StreamReceiver
    from classifier import classify_waste
    from overlay import draw_overlay, sample_center_hsv

WINDOW_TITLE = "Flood Robot - Drain Waste Classifier"


def main():
    try:
        receiver = StreamReceiver()
        receiver.open()
    except Exception:  # pragma: no cover - defensive
        receiver = None

    if receiver is None or receiver.cap is None or not receiver.cap.isOpened():
        print("Cannot open UDP stream. Check GStreamer install, matching IP/port (5002), "
              "same Wi-Fi, and that the robot is streaming.")
        return

    print("Receiving stream. Press 'q' to quit.")
    try:
        for frame in receiver.frames():
            hsv_avg = sample_center_hsv(frame)
            label = classify_waste(hsv_avg)
            draw_overlay(frame, label, hsv_avg)

            cv2.imshow(WINDOW_TITLE, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        receiver.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
