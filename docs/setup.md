# Ground-station setup (laptop side)

The ground station receives the robot's H.264 camera stream over UDP using
GStreamer, decodes it with OpenCV, and classifies drain blockages.

## Requirements

- **Python 3.7+**
- **GStreamer** installed on the laptop
- **OpenCV built WITH GStreamer support**

> ⚠️ The default `opencv-python` wheels from PyPI are typically built
> **without** GStreamer. If `cv2.VideoCapture(..., cv2.CAP_GSTREAMER)` fails to
> open the stream, this is the most common cause.

Check your OpenCV build:

```python
import cv2
print(cv2.getBuildInformation())   # look for "GStreamer: YES" under Video I/O
```

## Installing GStreamer

- **Windows:** Install the MSVC runtime + development installers from
  <https://gstreamer.freedesktop.org/download/> (runtime and development).
  Add the GStreamer `bin` folder to your `PATH`.
- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt install libgstreamer1.0-dev gstreamer1.0-plugins-{base,good,bad,ugly} \
                   gstreamer1.0-libav
  ```

If your OpenCV lacks GStreamer, build it from source with `-D WITH_GSTREAMER=ON`,
or use a conda-forge OpenCV that bundles GStreamer.

## Python dependencies

```bash
pip install -r requirements.txt
```

## Network configuration

The stream defaults must match the robot side (`flood_robot_pi.py`):

| Setting     | Value             |
|-------------|-------------------|
| Robot host  | `192.168.121.254` |
| UDP port    | `5002`            |
| Codec       | H.264 / RTP       |

Both devices must be on the **same Wi-Fi network**. Start the robot first, then
the ground station.

## Running

```bash
# from the repo root
python -m src.ground_station.main
# or
python src/ground_station/main.py
```

Press `q` in the video window to quit.

## View-only test (no classification)

Useful to confirm the stream itself works:

```bash
gst-launch-1.0 udpsrc port=5002 caps="application/x-rtp,media=video,\
encoding-name=H264,payload=96,clock-rate=90000" buffer-size=800000 \
! rtph264depay ! avdec_h264 ! videoflip method=2 ! autovideosink
```
