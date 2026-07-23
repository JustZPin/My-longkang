"""Frame-annotation concern ("other") for the ground station.

Samples the average HSV colour at the centre of a frame and draws the
classification result onto it. Pure OpenCV drawing, no stream/camera logic.
"""
import cv2

SAMPLE_HALF = 5   # half-size of the centre sample square (pixels)
MARKER_HALF = 10  # half-size of the drawn centre marker (pixels)


def sample_center_hsv(frame):
    """Return the average (H, S, V) of a small square at the frame centre."""
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    region = hsv[cy - SAMPLE_HALF:cy + SAMPLE_HALF,
                 cx - SAMPLE_HALF:cx + SAMPLE_HALF]
    return (int(region[:, :, 0].mean()),
            int(region[:, :, 1].mean()),
            int(region[:, :, 2].mean()))


def draw_overlay(frame, label, hsv_avg):
    """Draw the centre marker, blockage label, and HSV readout onto frame."""
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    cv2.rectangle(frame,
                  (cx - MARKER_HALF, cy - MARKER_HALF),
                  (cx + MARKER_HALF, cy + MARKER_HALF),
                  (0, 255, 0), 2)
    cv2.putText(frame, f"Blockage: {label}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"HSV {hsv_avg}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    return frame
