# My-longkang

Smart drain-monitoring robot with the **MyLongkang** app — an omni-wheel
Raspberry Pi robot that live-streams drains, flags rising water with LED/buzzer
flood alerts, and classifies blockages (paper, aluminium, glass).

> *"Longkang"* is the Malay/Singlish word for a drain or monsoon canal.

## System overview

The system has two sides that talk over Wi-Fi (UDP / H.264):

| Side | Runs on | Role |
|------|---------|------|
| **Robot** (`src/robot/`) | Raspberry Pi | PS2-driven omni-wheel base, ultrasonic water-distance sensing with LED/buzzer flood alerts, and H.264 camera stream-out. |
| **Ground station** (`src/ground_station/`) | Laptop | Receives the H.264 stream and classifies drain-blocking waste from the centre of the frame. |

Both sides talk over the same UDP H.264 link (`192.168.121.254:5002`): the robot
streams, the laptop receives and classifies.

## Repository layout

```
My-longkang/
├── README.md                 # this file
├── requirements.txt          # Python dependencies
├── LICENSE
├── .gitignore
├── src/
│   ├── ground_station/       # laptop side (split by concern)
│   │   ├── __init__.py
│   │   ├── config.py         # UDP port, flip method, GStreamer pipeline
│   │   ├── camera.py         # StreamReceiver — receive H.264 frames over UDP
│   │   ├── classifier.py     # classify_waste() — VER5 HSV rules
│   │   ├── overlay.py        # sample centre HSV + draw annotations
│   │   └── main.py           # entry point wiring the above together
│   └── robot/                # Raspberry Pi side (split by concern)
│       ├── __init__.py
│       ├── config.py         # GPIO pins, motor pins, stream host/port, thresholds
│       ├── sensors.py        # ultrasonic distance + LED tier + buzzer
│       ├── motion_ps2.py     # PS2 controller driver (primary)
│       ├── motion_ps2_alt.py # alternate PS2 bit-bang reader (reference)
│       ├── motors.py         # omni-wheel driver + PS2->motion mapping
│       ├── camera.py         # libcamera-vid -> UDP H.264 stream-out
│       └── main.py           # orchestration loop
├── scripts/
│   ├── stream_robot.sh       # Pi: libcamera-vid | gst udpsink
│   └── view_laptop.sh        # laptop: gst view-only receive
├── tests/
│   ├── test_classifier.py    # classifier unit tests (no camera needed)
│   ├── test_overlay.py       # overlay HSV sampling (needs OpenCV; else skipped)
│   └── test_motion.py        # PS2 -> motion control (fake GPIO, no hardware)
├── legacy/                   # archived, not in the live pipeline
│   └── on_robot_rgb_vision.py  # old on-Pi RGB detection (superseded by HSV)
└── docs/
    └── setup.md              # GStreamer / OpenCV install notes
```

## Quick start (ground station)

1. Install GStreamer and an OpenCV build **with GStreamer support** —
   see [docs/setup.md](docs/setup.md).
2. Install Python deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the robot so it begins streaming (see below).
4. Run the ground station:
   ```bash
   python -m src.ground_station.main
   # or
   python src/ground_station/main.py
   ```
5. Press `q` in the video window to quit.

## Quick start (robot / Raspberry Pi)

Requires a Raspberry Pi with `picamera2`, `RPi.GPIO`, OpenCV, GStreamer, and
`libcamera-apps`. Wiring (BCM pins) lives in
[src/robot/config.py](src/robot/config.py).

```bash
# option A: run the orchestration loop (stream + flood alerts + PS2 polling)
python -m src.robot.main

# option B: just start the video stream (shell one-liner)
bash scripts/stream_robot.sh
```

The robot's role breaks down as:

| Concern | Module | Notes |
|---------|--------|-------|
| Camera stream-out | [camera.py](src/robot/camera.py) | `libcamera-vid` → RTP/UDP H.264 to the laptop |
| Flood alert | [sensors.py](src/robot/sensors.py) | HC-SR04 distance → RED/YELLOW/GREEN LED + buzzer |
| Motion input | [motion_ps2.py](src/robot/motion_ps2.py) | PS2 controller, bit-banged over GPIO |
| Motion drive | [motors.py](src/robot/motors.py) | maps PS2 buttons → omni-wheel speeds → H-bridge PWM |

### Driving controls (PS2)

| Button | Motion |
|--------|--------|
| D-pad Up / Down | forward / reverse |
| D-pad Left / Right | strafe left / right |
| L1 / R1 | rotate left / right |

Diagonals work (e.g. Up + Right). Drive is a **4-wheel omni base on L298N
H-bridges** (one channel per wheel: in1/in2 + PWM enable); motor pins are in
[src/robot/config.py](src/robot/config.py) (`MOTORS`) — set them to match your
wiring. The whole PS2 → motion path
is unit-tested with a fake GPIO in
[tests/test_motion.py](tests/test_motion.py), so the logic is verified without
a Pi or motors attached.

## How blockage classification works

The classifier samples the average HSV colour in a small square at the centre of
each frame and maps it to a likely drain-blocking material:

| Label              | Rough colour cue          |
|--------------------|---------------------------|
| Paper (White)      | low saturation, bright    |
| Aluminium (Red)    | red hue, saturated        |
| Aluminium (Blue)   | blue hue, saturated       |
| Glass (Green)      | green hue                 |
| Glass (Black)      | low saturation, dark      |
| Other (Yellow)     | yellow hue, very saturated|
| Other Waste        | anything else             |

The rules live in [src/ground_station/classifier.py](src/ground_station/classifier.py)
and are covered by [tests/test_classifier.py](tests/test_classifier.py).

> **One colour path:** classification is **HSV, on the laptop only**. An older
> on-robot **RGB** detector existed but is superseded and archived under
> [legacy/](legacy/) — it was never part of the streaming pipeline.

## Configuration

Stream settings default to the working robot setup and live in
[src/ground_station/config.py](src/ground_station/config.py):

| Setting     | Default           |
|-------------|-------------------|
| Robot host  | `192.168.121.254` |
| UDP port    | `5002`            |
| Flip method | `2` (180°)        |

Both devices must be on the same Wi-Fi network, and the port must match the robot.

## Running the tests

```bash
python -m pytest
```

The classifier tests are pure functions and need no camera or GStreamer.

## License

[MIT](LICENSE)
