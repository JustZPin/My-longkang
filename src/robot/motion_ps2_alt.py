"""PS2 controller driver (alternate bit-bang reader) — kept for reference.

A simpler SEL-based bit-bang implementation that also reads the left analog
stick and validates the 0x5A response header. Uses pull-ups on DATA/ACK and an
optional ACK line. Kept verbatim from the second shared script (pins via config)
so both working variants are preserved; motion_ps2.py is the primary driver.
"""
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from . import config

# —— Timing (≈10 µs) ——
DELAY = 10e-6


def setup():
    if GPIO is None:
        raise RuntimeError("RPi.GPIO not available - run this on the Raspberry Pi.")
    GPIO.setmode(GPIO.BCM)
    # inputs with pull-ups
    GPIO.setup(config.PS2_DATA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PS2_ACK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # outputs, idle HIGH
    for pin in (config.PS2_CMD, config.PS2_ATT, config.PS2_CLK):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)


def transfer_byte(cmd):
    """Send one byte and read one byte back, LSB first."""
    result = 0
    for bit in range(8):
        GPIO.output(config.PS2_CLK, GPIO.LOW)

        GPIO.output(config.PS2_CMD, GPIO.HIGH if (cmd >> bit) & 1 else GPIO.LOW)
        time.sleep(DELAY)

        _ = GPIO.input(config.PS2_ACK)  # read ACK line if desired

        GPIO.output(config.PS2_CLK, GPIO.HIGH)
        if GPIO.input(config.PS2_DATA):
            result |= (1 << bit)
        time.sleep(DELAY)
    return result


def read_controller():
    """Drive SEL low, send the 8-byte PS2 command, then release SEL."""
    GPIO.output(config.PS2_ATT, GPIO.LOW)
    time.sleep(DELAY)
    resp = [transfer_byte(b)
            for b in (0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)]
    GPIO.output(config.PS2_ATT, GPIO.HIGH)
    return resp


def _demo():
    setup()
    print("PSX bit-bang receiver starting…")
    time.sleep(0.1)
    try:
        while True:
            data = read_controller()
            if data[1] != 0x5A:               # valid response header
                print("Controller lost")
                time.sleep(0.5)
                continue

            btn_word = (~(data[3] | (data[4] << 8))) & 0xFFFF  # active-low
            print(f"Buttons: 0x{btn_word:04X}")
            print(f"Analog L: x={data[5]}  y={data[6]}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    _demo()
