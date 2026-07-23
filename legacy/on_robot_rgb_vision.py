"""On-robot colour detection (RGB) — kept verbatim from the robot script.

This is the Pi-side vision path: it highlights red/green/blue blobs and does a
black/white threshold directly on the camera frame. Note this uses **RGB**
thresholds, unlike the laptop ground-station classifier which works in HSV.

Pure OpenCV/numpy — no GPIO — so it can run and be tested off-Pi.
"""
import cv2
import numpy as np


def detect_red_rgb(frame):
    lower_red = np.array([150, 0, 0])
    upper_red = np.array([255, 100, 100])
    return highlight_color(frame, lower_red, upper_red, (255, 0, 0))


def detect_green_rgb(frame):
    lower_green = np.array([0, 150, 0])
    upper_green = np.array([100, 255, 100])
    return highlight_color(frame, lower_green, upper_green, (0, 255, 0))


def detect_blue_rgb(frame):
    lower_blue = np.array([0, 0, 150])
    upper_blue = np.array([100, 100, 255])
    return highlight_color(frame, lower_blue, upper_blue, (0, 0, 255))


def highlight_color(frame, lower, upper, circle_color):
    mask = cv2.inRange(frame, lower, upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        (x, y), radius = cv2.minEnclosingCircle(c)
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), circle_color, 3)
    return frame


def detect_black_white(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return bw
