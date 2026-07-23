# legacy / archived code

Code kept for reference but **not part of the live system**.

## `motion_ps2_pi.py` and `motion_ps2_pi_alt.py`

Raspberry-Pi (`RPi.GPIO`) bit-bang PS2 controller readers. Locomotion now runs
on the **Arduino Uno R3** (see [firmware/arduino/](../firmware/arduino/)), which
reads the PS2 controller and drives the L293D motor drivers directly, so these
Pi-side readers are superseded.

The omni-wheel mixing they fed into is preserved and unit-tested in
`src/robot/motors.py` — the Arduino firmware mirrors those equations.
