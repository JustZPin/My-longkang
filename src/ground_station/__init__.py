"""Project 2 — Flood-robot ground station (laptop side).

Receives the robot's H.264 camera stream over UDP (GStreamer) and classifies
drain-blocking waste (Paper / Aluminium / Glass) from the centre region.

Concerns are split across modules:
  config      - ports, flip method, GStreamer pipeline
  camera      - receive H.264 frames over UDP (StreamReceiver)
  classifier  - map centre HSV to a drain-blockage material (classify_waste)
  overlay     - sample centre HSV + draw annotations
  main        - wire the above together
"""

__all__ = ["classify_waste", "StreamReceiver", "sample_center_hsv", "draw_overlay"]

from .classifier import classify_waste

# overlay and camera import cv2 at module load; keep the package importable in a
# headless/minimal environment (e.g. CI running only the classifier tests) where
# OpenCV/GStreamer may not be installed.
try:
    from .overlay import draw_overlay, sample_center_hsv
except Exception:  # pragma: no cover
    draw_overlay = sample_center_hsv = None

try:
    from .camera import StreamReceiver
except Exception:  # pragma: no cover
    StreamReceiver = None
