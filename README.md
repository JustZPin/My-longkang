# LongKang Hero × MyLongkang

**Smart, modular flood-mitigation system that stops flooding at its root — the
blocked drain.** An omni-wheel robot (**LongKang Hero**) patrols drains,
detects and clears waste blockages, and streams live status to a mobile app
(**MyLongkang**) for real-time monitoring and alerts.

> *"Longkang"* is the Malay/Singlish word for a drain or monsoon canal.

**Team EEyerrr — Universiti Malaya** · Edmat-46 · Problem Statement No. 3
Chua Zhu Heng (Leader) · Lim Zhi Pin · Low Jia Qi · Chin Pei Kang

Aligned with **UN SDG 6** (Clean Water & Sanitation), **SDG 11** (Sustainable
Cities & Communities), and **SDG 13** (Climate Action).

---

## The problem: when drains fail, cities drown

- **17** flood hotspots and **171** flood-prone locations across **11**
  parliamentary constituencies in Kuala Lumpur (DBKL).
- Some city drains now carry only **half** their designed capacity, mainly from
  **silt and garbage accumulation**.
- Malaysia's flood-related losses reached **RM933.4 million in 2024** (up from
  RM755.4M in 2023) — about **0.05% of nominal GDP**. Losses fall on living
  quarters (42.2%), public assets & infrastructure (35.3%), and agriculture
  (22.5%).
- The 2021–2022 floods left **54 dead**, displaced **71,000+**, and affected
  **125,000+** people.

Blocked drains are an upstream, addressable cause. LongKang Hero targets it
directly.

## The solution: from detection to action

A modular smart system that **identifies** and **clears** drain blockages
before they escalate into floods — through rapid response and real-time
monitoring. Four feature pillars:

| Mode | Pillar | What it does |
|------|--------|--------------|
| Active | **Drain monitoring** | Live camera + processing on Raspberry Pi 5 |
| Active | **Blockage detection** | Ultrasonic distance → LED tier + buzzer alerts |
| Active | **Clearing the obstruction** | High-pressure water jet flushes the blockage |
| Passive | **Mobile app integration** | Live data, alerts & maps in MyLongkang |

---

## Repository layout

This repo contains the **software**: the Raspberry-Pi robot control code and the
laptop ground-station classifier.

```
LongKang-Hero/
├── README.md
├── requirements.txt          # laptop / ground-station deps
├── requirements-robot.txt    # Raspberry Pi deps
├── LICENSE · .gitignore · pytest.ini
├── src/
│   ├── ground_station/       # laptop side — receives stream, classifies waste
│   │   ├── config.py         # UDP port, flip method, GStreamer pipeline
│   │   ├── camera.py         # StreamReceiver — receive H.264 frames over UDP
│   │   ├── classifier.py     # classify_waste() — HSV rules
│   │   ├── overlay.py        # sample centre HSV + draw annotations
│   │   └── main.py           # entry point
│   └── robot/                # Raspberry Pi 5 side
│       ├── config.py         # GPIO pins, motor pins, stream host/port, thresholds
│       ├── sensors.py        # HC-SR04 distance + RED/YELLOW/GREEN LED + buzzer
│       ├── vision.py         # on-robot RGB drain monitoring (leaves vs rubbish)
│       ├── motors.py         # omni-wheel mixing spec (mirrored by Arduino firmware)
│       ├── camera.py         # libcamera-vid -> UDP H.264 stream-out
│       └── main.py           # sensing + streaming orchestration
├── firmware/
│   └── arduino/              # Arduino Uno R3 locomotion (PS2 -> 2x L293D -> 4 wheels)
│       └── longkang_locomotion/longkang_locomotion.ino
├── scripts/                  # stream_robot.sh · view_laptop.sh
├── tests/                    # classifier, overlay, motion (fake GPIO) — pytest
└── legacy/                   # archived Pi-side PS2 readers (superseded by Arduino)
```

> **Scope note:** the water-jet actuation control and the MyLongkang mobile app
> are part of the wider system but are **not** in this repository yet. See
> [Hardware](#the-hardware-longkang-hero) and [MyLongkang app](#the-app-mylongkang).

## Running the software

**Locomotion (Arduino Uno R3)** — flash the sketch (needs the `PS2X_lib`
library); see [firmware/arduino/](firmware/arduino/):
```bash
arduino-cli compile --fqbn arduino:avr:uno firmware/arduino/longkang_locomotion
arduino-cli upload  --fqbn arduino:avr:uno -p <PORT> firmware/arduino/longkang_locomotion
```

**Robot (Raspberry Pi 5)** — needs `picamera2`, `RPi.GPIO`, OpenCV, GStreamer,
`libcamera-apps`:
```bash
pip install -r requirements-robot.txt
python -m src.robot.main            # flood-alert sensing + H.264 stream
python -m src.robot.vision          # on-Pi RGB drain monitoring (leaves vs rubbish)
# or just start the video stream:
bash scripts/stream_robot.sh
```

**Ground station (laptop)** — needs OpenCV built **with GStreamer**
(see [docs/setup.md](docs/setup.md)):
```bash
pip install -r requirements.txt
python -m src.ground_station.main  # receive + classify; press q to quit
```

**Tests** (no hardware needed):
```bash
python -m pytest
```

---

## The hardware: LongKang Hero

Bill of materials for **Prototype_01** — total **≈ RM 1,238**.

| Subsystem | Key parts |
|-----------|-----------|
| **Compute** | Raspberry Pi 5 · Pi Camera Module 3 |
| **Locomotion** | PS2 wireless controller → Arduino Uno R3 → 2× **L293D** → 4× TT motor → 4× omni wheel |
| **Sensing / alerts** | HC-SR04 ultrasonic · Red/Yellow/Green LEDs · passive buzzer |
| **Clearing (water jet)** | water reservoir + silicone tubing → **FL-3201 diaphragm pump (~60–100 PSI)** → 12V normally-closed solenoid valve → focused high-pressure nozzle |
| **Waterproofing** | TICONN junction box · PCB conformal coating · Pi Camera protective dome · heat-shrink + silicone sealant |
| **Water-based (target design)** | HDPE + foam-reinforced floating base · 2× IPX8 underwater thrusters · directional steering fins |

### How blockage detection works

The HC-SR04 measures the distance to the nearest obstruction and drives a
traffic-light alert. Thresholds live in
[src/robot/config.py](src/robot/config.py) and match the deck:

| Zone | Distance | LED | Meaning |
|------|----------|-----|---------|
| Safe | 2–3 m | 🟢 Green | Obstruction far — no action |
| Caution | 1–2 m | 🟡 Yellow | Approaching — prepare to slow |
| Critical | 0–1 m | 🔴 Red | Very close — immediate action |

The buzzer emits distinct patterns per zone. The Pi Camera adds visual
confirmation of debris/rubbish and water-flow anomalies (see
[colour detection](#drain-monitoring-vision-rgb) below).

### How clearing works

When the ultrasonic sensor and camera confirm a blockage, the Raspberry Pi 5
triggers the pump + solenoid valve to fire a focused water jet through the
nozzle, and simultaneously raises a **visual alert** (LED), **sound alert**
(buzzer), and pushes **real-time data to MyLongkang**.

### Driving controls (PS2 → Arduino Uno)

Locomotion is a self-contained **Arduino Uno R3** sketch
([firmware/arduino/](firmware/arduino/)): it reads the PS2 controller and drives
the two L293D boards.

| Button | Motion |
|--------|--------|
| D-pad Up / Down | forward / reverse |
| D-pad Left / Right | strafe left / right |
| L1 / R1 | rotate left / right |

Diagonals work (e.g. Up+Right). The omni-wheel mixing in the sketch is the same
logic defined and unit-tested in Python
([motors.py](src/robot/motors.py) / [tests/test_motion.py](tests/test_motion.py))
— no Pi or motors needed to verify the maths.

### Drain-monitoring vision (RGB)

The active vision path is **on-robot RGB detection**
([vision.py](src/robot/vision.py)), matching the deck's "Drain Monitoring
System":

| Colour | Meaning |
|--------|---------|
| 🔴 Red | Dry / semi-wet leaves & plant material |
| 🔵 Blue | Rubbish |

Run it live on the Pi with `python -m src.robot.vision`. A separate laptop
ground-station classifier ([classifier.py](src/ground_station/classifier.py))
also exists for the UDP-stream path and works in HSV (Paper / Aluminium / Glass).

---

## The app: MyLongkang

A Flutter/Dart mobile app (Firebase backend, Google Maps API) — Phase_01 BOM
**≈ RM 866/setup**. Features shown in the deck:

- **Push notifications** — real-time alerts when a robot detects a heavily or
  slightly blocked drain, even when the app is closed.
- **Real-time drain-condition map** — colour-coded segments: 🟢 no blockage,
  🟡 slightly blocked, 🔴 heavily blocked, plus robot **centerpoints**.
- **Robot location tracking** — live position of each robot on the map.
- **Robot & drain info pages** (Red / Yellow / Green status) — real-time
  monitoring feed, battery level, signal strength, last maintenance date, last
  inspection time, urgency level, and drain status.
- **Drain history log** — past inspections and blockage levels for trend
  analysis and preventive maintenance.
- **Issue reporting** and **centerpoint integration** for coordinated,
  scalable deployment.

---

## Competitive advantage

Against Bandicoot Mini, Sewer Robotics and general pipe cleaners, LongKang Hero
is the only option combining **all** of: real-time mobile-app integration,
camera visual monitoring, sensor-based blockage detection, water-jet cleaning,
integrated LED/buzzer alerts, AI-ready predictive maintenance, and a compact,
portable design.

## Roadmap

- **AI-powered blockage classification** — auto-classify plastic / sediment /
  vegetation from captured images.
- **Environmental monitoring** — water level, temperature & humidity, water pH.
- **Thermal vision** — FLIR Lepton 3.5 + PureThermal 2 for low-light/heat
  analysis.
- **Extendable arm / probe** — reach into water without immersing the body.
- **Vision beyond flooding** — evolve into a smart tunnel-exploration and
  underground-mapping platform (live feed + sensor-fusion mapping + AI-assisted
  navigation).

## Alliances

Government (DBKL, PLANMalaysia, JPS — Dept. of Irrigation & Drainage) and
Universiti Malaya (JPPHB UM, Jabatan Keselamatan, UM Sustainable Development
Centre).

## License

[MIT](LICENSE) · Presented by Team EEyerrr, Universiti Malaya.
