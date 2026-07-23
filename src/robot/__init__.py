"""Flood robot (Raspberry Pi side).

Streams the drain camera to the laptop ground station, raises LED/buzzer flood
alerts from an ultrasonic water-distance reading, and is driven by a PS2
controller (bit-banged over GPIO).

Modules:
  config          - GPIO pins, stream host/port, LED thresholds
  sensors         - ultrasonic distance, LED tier, buzzer
  motion_ps2      - PS2 controller driver (primary)
  motion_ps2_alt  - alternate PS2 bit-bang reader (kept for reference)
  motors          - omni-wheel motor driver + PS2->motion mapping
  camera          - libcamera-vid -> UDP H.264 stream-out
  main            - orchestration loop

Modules import RPi.GPIO lazily so the package can be imported off-Pi without it.
Colour classification lives on the laptop (HSV); the old on-robot RGB path is
archived under legacy/.
"""
