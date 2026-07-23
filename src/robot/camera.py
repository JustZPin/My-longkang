"""Camera stream-out for the robot (Pi side).

Launches libcamera-vid and pipes H.264 over RTP/UDP to the laptop ground
station. This is the sender that matches ground_station.camera.StreamReceiver.

The exact shell one-liner is also in scripts/stream_robot.sh.
"""
import subprocess

from . import config


def build_stream_command(host: str = config.STREAM_HOST,
                         port: int = config.STREAM_PORT,
                         width: int = config.FRAME_WIDTH,
                         height: int = config.FRAME_HEIGHT) -> str:
    """Return the libcamera-vid | gst-launch pipe as a shell command string."""
    return (
        f"libcamera-vid -t 0 --width {width} --height {height} -n --inline "
        f"--codec h264 --profile baseline -o - "
        f"| gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 "
        f"! udpsink host={host} port={port}"
    )


def start_stream(**kwargs) -> subprocess.Popen:
    """Start streaming in a child process. Returns the Popen handle.

    Call .terminate() on the returned handle to stop streaming.
    """
    cmd = build_stream_command(**kwargs)
    return subprocess.Popen(cmd, shell=True)


if __name__ == "__main__":
    print(build_stream_command())
