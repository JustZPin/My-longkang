#!/usr/bin/env python3
"""Flood robot (Raspberry Pi 5) — orchestration entry point.

The Pi handles sensing, camera and alerting; **locomotion runs independently on
the Arduino Uno R3** (PS2 -> 2x L293D -> 4 omni wheels, see firmware/arduino/),
so there is no motor/PS2 code in this loop.

  sensors.read_ultrasonic_distance / update_leds / buzzer -> flood alerting
  camera.start_stream                                     -> H.264 UDP stream

For live on-Pi RGB drain monitoring (leaves vs rubbish) run the vision module
instead:  python -m src.robot.vision
"""
import time

try:
    from . import camera, sensors
    from . import config
except ImportError:  # run as a script
    import camera
    import config
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
    stream = camera.start_stream()
    print(f"Streaming to {config.STREAM_HOST}:{config.STREAM_PORT}. Ctrl+C to stop.")

    try:
        while True:
            distance = sensors.read_ultrasonic_distance()
            handle_flood_alert(distance)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.terminate()
        sensors.buzzer_off()
        sensors.cleanup()


if __name__ == "__main__":
    main()
