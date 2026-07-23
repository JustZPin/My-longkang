"""On-robot drain-monitoring vision (RGB) — LongKang Hero's active colour path.

Runs on the Raspberry Pi and highlights coloured waste directly on the camera
frame using **RGB** thresholds, matching the deck's "Drain Monitoring System":

    Red  -> dry / semi-wet leaves & plant material
    Blue -> rubbish

The detection functions are pure OpenCV/numpy (no GPIO), so they run and are
tested off-Pi. run() adds a live capture loop for the Pi (picamera2, else a
regular camera via cv2.VideoCapture).
"""
import cv2
import numpy as np

# What each detected colour means for a drain blockage (from the deck).
LEGEND = {
    "Red": "Leaves / plant material",
    "Blue": "Rubbish",
}


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


def annotate(frame):
    """Run all RGB detectors on a frame and return the annotated frame."""
    frame = detect_red_rgb(frame)
    frame = detect_green_rgb(frame)
    frame = detect_blue_rgb(frame)
    return frame


def _open_camera():
    """Return a frame-grabber callable. Prefers picamera2, falls back to cv2."""
    try:
        from picamera2 import Picamera2  # Pi camera
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"format": "RGB888", "size": (640, 480)}))
        picam.start()
        return lambda: picam.capture_array(), picam.stop
    except Exception:
        cap = cv2.VideoCapture(0)
        return (lambda: cap.read()[1]), cap.release


def run():
    """Live on-Pi RGB drain-monitoring loop (press 'q' to quit)."""
    grab, close = _open_camera()
    print("RGB drain monitoring. Legend:", LEGEND, "- press 'q' to quit.")
    try:
        while True:
            frame = grab()
            if frame is None:
                continue
            cv2.imshow("LongKang Hero - Drain Monitoring (RGB)", annotate(frame))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
