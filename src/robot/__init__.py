"""LongKang Hero — Raspberry Pi 5 side.

Streams the drain camera, raises LED/buzzer flood alerts from an ultrasonic
water-distance reading, and runs on-robot RGB drain monitoring. Locomotion runs
separately on an Arduino Uno R3 (see firmware/arduino/).

Modules:
  config      - GPIO pins, motor pins (Pi-drive option), stream host/port, thresholds
  sensors     - ultrasonic distance, LED tier, buzzer
  vision      - on-robot RGB drain monitoring (leaves vs rubbish)
  motors      - omni-wheel mixing spec (mirrored by the Arduino firmware)
  camera      - libcamera-vid -> UDP H.264 stream-out
  main        - sensing + streaming orchestration loop

Modules import RPi.GPIO / cv2 lazily so the package imports off-Pi.
The old Raspberry-Pi PS2 readers are archived under legacy/ now that the
Arduino owns locomotion.
"""
