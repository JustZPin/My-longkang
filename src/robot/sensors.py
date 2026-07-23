"""Flood-alert sensors + indicators for the robot (Pi side).

Ultrasonic water-distance reading, the RED/YELLOW/GREEN LED tier, and the
passive buzzer. Logic kept verbatim from the working robot script; the only
change is that GPIO setup is moved into setup() (instead of running at import)
so the module can be imported off-Pi and the pins come from config.
"""
import time

try:
    import RPi.GPIO as GPIO
except ImportError:  # allow importing on a non-Pi machine
    GPIO = None

from . import config

_pwm = None  # buzzer PWM handle, created in setup()


def _require_gpio():
    if GPIO is None:
        raise RuntimeError("RPi.GPIO not available - run this on the Raspberry Pi.")


def setup():
    """Configure GPIO pins and the buzzer PWM. Call once at startup."""
    _require_gpio()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.TRIG_PIN, GPIO.OUT)
    GPIO.setup(config.ECHO_PIN, GPIO.IN)
    GPIO.setup(config.RED, GPIO.OUT)
    GPIO.setup(config.YELLOW, GPIO.OUT)
    GPIO.setup(config.GREEN, GPIO.OUT)
    GPIO.setup(config.BUZZER_PIN, GPIO.OUT)

    global _pwm
    _pwm = GPIO.PWM(config.BUZZER_PIN, 1)  # initial dummy frequency


# === Ultrasonic Distance Function ===
def read_ultrasonic_distance():
    """Return distance in cm, or float('inf') if out of the 2-400 cm range."""
    GPIO.output(config.TRIG_PIN, False)
    time.sleep(0.05)

    GPIO.output(config.TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(config.TRIG_PIN, False)

    pulse_start = time.time()
    timeout = pulse_start + 0.04
    while GPIO.input(config.ECHO_PIN) == 0 and time.time() < timeout:
        pulse_start = time.time()

    pulse_end = time.time()
    timeout = pulse_end + 0.04
    while GPIO.input(config.ECHO_PIN) == 1 and time.time() < timeout:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    if distance < 2 or distance > 400:
        return float('inf')
    return round(distance, 2)


# === LED Control ===
def update_leds(distance):
    """Light exactly one LED based on how close the water surface is."""
    GPIO.output(config.RED, GPIO.LOW)
    GPIO.output(config.YELLOW, GPIO.LOW)
    GPIO.output(config.GREEN, GPIO.LOW)

    if distance <= config.RED_THRESHOLD:
        GPIO.output(config.RED, GPIO.HIGH)
    elif distance <= config.YELLOW_THRESHOLD:
        GPIO.output(config.YELLOW, GPIO.HIGH)
    elif distance <= config.GREEN_THRESHOLD:
        GPIO.output(config.GREEN, GPIO.HIGH)


# === Buzzer ===
# NOTE: the original script set up the PWM object and beep-timing variables but
# the full beep loop was not included in the shared code. These helpers drive
# the same PWM object; tune frequency/cadence in main.py as needed.
def buzzer_on(frequency=1000):
    """Start the passive buzzer at the given frequency (Hz)."""
    _pwm.ChangeFrequency(frequency)
    _pwm.start(50)  # 50% duty cycle


def buzzer_off():
    """Silence the buzzer."""
    _pwm.stop()


def cleanup():
    """Release GPIO resources."""
    if GPIO is not None:
        GPIO.cleanup()
