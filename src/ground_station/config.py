"""Stream configuration for the flood-robot ground station.

These values must match the robot side (flood_robot_pi.py). The robot streams
H.264 over UDP to the laptop; the defaults below match the working setup:
host 192.168.121.254, port 5002.
"""

UDP_PORT = 5002        # must match the robot
FLIP_METHOD = 2        # 0 none | 1 cw90 | 2 180 | 3 ccw90 | 4 hflip | 5 vflip


def build_receive_pipeline(port: int = UDP_PORT, flip_method: int = FLIP_METHOD) -> str:
    """Return the GStreamer pipeline string used by cv2.VideoCapture.

    Requires OpenCV built WITH GStreamer support and GStreamer installed on the
    laptop (see docs/setup.md). Start the robot (flood_robot_pi.py) first.
    """
    return (
        f"udpsrc port={port} "
        f'caps="application/x-rtp,media=video,encoding-name=H264,'
        f'payload=96,clock-rate=90000" '
        f"buffer-size=800000 ! rtph264depay ! avdec_h264 "
        f"! videoflip method={flip_method} "
        f"! videoconvert ! appsink drop=true sync=false"
    )


# Prebuilt pipeline for the default configuration.
GST_RECV = build_receive_pipeline()
