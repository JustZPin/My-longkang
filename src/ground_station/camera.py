"""Camera / stream-receive concern for the ground station.

Wraps opening the robot's UDP H.264 stream via GStreamer and reading frames.
Kept separate from classification and drawing so each concern is testable and
swappable (e.g. point it at a file or a local webcam for offline testing).
"""
import cv2

from .config import GST_RECV


class StreamReceiver:
    """Receive frames from the robot's UDP H.264 stream.

    Usage:
        with StreamReceiver() as cam:
            for frame in cam.frames():
                ...
    """

    def __init__(self, pipeline: str = GST_RECV, backend: int = cv2.CAP_GSTREAMER):
        self.pipeline = pipeline
        self.backend = backend
        self.cap = None

    def open(self) -> bool:
        """Open the capture. Returns True on success."""
        self.cap = cv2.VideoCapture(self.pipeline, self.backend)
        return self.cap.isOpened()

    def read(self):
        """Read a single frame. Returns (ret, frame) like cv2.VideoCapture."""
        return self.cap.read()

    def frames(self):
        """Yield frames as they arrive, skipping dropped reads."""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                continue
            yield frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __enter__(self):
        if not self.open():
            raise RuntimeError(
                "Cannot open UDP stream. Check GStreamer install, matching "
                "IP/port (5002), same Wi-Fi, and that the robot is streaming."
            )
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
