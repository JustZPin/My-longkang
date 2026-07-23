#!/usr/bin/env python3
"""Flood robot (Raspberry Pi side) — orchestration entry point.

Wires the working pieces together:
  camera.start_stream       -> stream H.264 to the laptop ground station
  sensors.read_ultrasonic_distance / update_leds / buzzer -> flood alerting
  motion_ps2.poll_controller / decode_buttons -> read PS2 controller for driving

NOTE: this main loop is integration glue. The individual drivers (sensors,
motion_ps2, camera) are your verbatim working code; motors.py + the PS2->motion
mapping make the base moveable. Motor pins are assumed (config.MOTORS) — set
them to match your wiring.
"""
import time

try:
    from . import camera, motion_ps2, motors, sensors
    from . import config
except ImportError:  # run as a script
    import camera
    import config
    import motion_ps2
    import motors
    import sensors


def handle_flood_alert(distance):
    """Update the LED tier and sound the buzzer when water is dangerously close."""
    sensors.update_leds(distance)
    if distance <= config.RED_THRESHOLD:
        sensors.buzzer_on(2000)
    else:
        sensors.buzzer_off()


def main():
    sensors.setup()
    motion_ps2.setup()
    motor_ctl = motors.MotorController()
    motor_ctl.setup()
    stream = camera.start_stream()
    print(f"Streaming to {config.STREAM_HOST}:{config.STREAM_PORT}. Ctrl+C to stop.")

    try:
        while True:
            # --- flood alerting ---
            distance = sensors.read_ultrasonic_distance()
            handle_flood_alert(distance)

            # --- motion (PS2 -> omni wheels) ---
            data = motion_ps2.poll_controller()
            if data:
                pressed = motion_ps2.decode_buttons(data)
                motors.drive(motor_ctl, pressed)

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.terminate()
        motor_ctl.cleanup()
        sensors.buzzer_off()
        sensors.cleanup()


if __name__ == "__main__":
    main()
