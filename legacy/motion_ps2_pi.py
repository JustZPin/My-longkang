"""PS2 controller driver (primary) — motion input for the robot.

Bit-bangs the PS2 protocol over GPIO and decodes the digital buttons, plus a
pairing helper for wireless receivers. Logic kept verbatim from the working
script; pins now come from config and GPIO setup is in setup().

This reads the controller. Feeding button state to the omni-wheel motors is
done in main.py (motor-driver code was not part of the shared source).
"""
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from . import config

BUTTONS = [
    "Select", "L3", "R3", "Start", "Up", "Right", "Down", "Left",
    "L2", "R2", "L1", "R1", "Triangle", "Circle", "Cross", "Square",
]


def setup():
    """Configure PS2 GPIO lines. Idle state HIGH on the driven lines."""
    if GPIO is None:
        raise RuntimeError("RPi.GPIO not available - run this on the Raspberry Pi.")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.PS2_CMD, GPIO.OUT)
    GPIO.setup(config.PS2_CLK, GPIO.OUT)
    GPIO.setup(config.PS2_ATT, GPIO.OUT)
    GPIO.setup(config.PS2_PAIR, GPIO.OUT)
    GPIO.setup(config.PS2_DATA, GPIO.IN)

    GPIO.output(config.PS2_CMD, True)
    GPIO.output(config.PS2_CLK, True)
    GPIO.output(config.PS2_ATT, True)
    GPIO.output(config.PS2_PAIR, True)  # idle HIGH


# === Microsecond Delay ===
def delay_us(microseconds):
    time.sleep(microseconds / 1_000_000)


# === Bit Transfer (1 byte out, 1 byte in) ===
def shift_out_in(byte_out):
    byte_in = 0
    for i in range(8):
        GPIO.output(config.PS2_CMD, (byte_out >> i) & 1)
        GPIO.output(config.PS2_CLK, False)
        delay_us(15)

        if GPIO.input(config.PS2_DATA):
            byte_in |= (1 << i)

        GPIO.output(config.PS2_CLK, True)
        delay_us(15)
    return byte_in


# === Send a Full Command to the PS2 controller ===
def send_command(cmd_bytes):
    response = []
    GPIO.output(config.PS2_ATT, False)
    delay_us(20)

    for b in cmd_bytes:
        response.append(shift_out_in(b))

    GPIO.output(config.PS2_ATT, True)
    delay_us(20)
    return response


# === Poll Controller ===
def poll_controller():
    return send_command([0x01, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


# === Decode Digital Buttons ===
def decode_buttons(data):
    if len(data) < 5:
        return []
    button_bytes = data[3], data[4]
    pressed = []
    for i in range(16):
        byte_index = i // 8
        bit_index = i % 8
        if not (button_bytes[byte_index] & (1 << bit_index)):
            pressed.append(BUTTONS[i])
    return pressed


# === Trigger Pairing Mode ===
def trigger_pairing():
    print("Triggering pairing mode... Hold new controller's pair button now!")
    GPIO.output(config.PS2_PAIR, False)  # pull pairing pin LOW
    time.sleep(1.5)                       # hold for 1.5 seconds
    GPIO.output(config.PS2_PAIR, True)    # return to HIGH
    print("Pairing signal sent. Watch for blinking green LED...")


def _demo():
    """Standalone test loop (original __main__ behaviour)."""
    setup()
    input("Press ENTER to pair with new controller...")
    trigger_pairing()
    time.sleep(3)

    print("\nPolling PS2 controller receiver...\nPress buttons to test.")
    try:
        while True:
            data = poll_controller()
            if data:
                mode = data[1]
                if mode == 0x41:
                    print("Mode: Digital")
                elif mode == 0x73:
                    print("Mode: Analog")

                buttons = decode_buttons(data)
                if buttons:
                    print("Pressed:", buttons)
            else:
                print("No response.")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Exiting...")
        GPIO.cleanup()


if __name__ == "__main__":
    _demo()
