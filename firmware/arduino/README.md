# LongKang Hero — Arduino locomotion firmware

Locomotion runs on an **Arduino Uno R3** (per the pitch deck's *Prototype
Locomotion*): the PS2 wireless controller and the two **L293D** motor drivers are
wired to the Uno, which drives the 4 TT motors / omni wheels. The Raspberry Pi 5
handles sensing, camera, clearing, and app comms separately.

## Sketch

[`longkang_locomotion/longkang_locomotion.ino`](longkang_locomotion/longkang_locomotion.ino)

The omni-wheel mixing in the sketch is the **same** logic that is unit-tested in
Python (`src/robot/motors.py` → `buttons_to_velocity` + `mix`,
`tests/test_motion.py`). If you change one, change the other.

## Dependencies

- Arduino IDE (or `arduino-cli`)
- **PS2X_lib** by Bill Porter — Library Manager, or
  <https://github.com/madsci1016/Arduino-PS2X>

## Wiring (default pins)

| Signal | Uno pin |
|--------|---------|
| PS2 DAT / CMD / SEL / CLK | 12 / 11 / 10 / 13 |
| FL motor in1 / in2 / EN (PWM) | 2 / 4 / 3 |
| FR motor in1 / in2 / EN (PWM) | 7 / 8 / 5 |
| RL motor in1 / in2 / EN (PWM) | A0 / A1 / 6 |
| RR motor in1 / in2 / EN (PWM) | A2 / A3 / 9 |

Enable pins must be PWM-capable. Remove the L293D `EN` jumpers so PWM controls
speed. Adjust the pin map at the top of the sketch to match your build.

## Flashing

```bash
# with arduino-cli
arduino-cli compile --fqbn arduino:avr:uno firmware/arduino/longkang_locomotion
arduino-cli upload  --fqbn arduino:avr:uno -p <PORT> firmware/arduino/longkang_locomotion
```

## Controls

D-pad Up/Down = forward/reverse · D-pad Left/Right = strafe · L1/R1 = rotate.
Diagonals (e.g. Up+Right) work.
