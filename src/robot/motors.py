"""Omni-wheel motor driver + PS2-button -> motion mapping.

Two layers, kept separate so the *logic* is testable without hardware:

  1. Pure functions (no GPIO):
       buttons_to_velocity(pressed) -> (vx, vy, omega)
       mix(vx, vy, omega)           -> (fl, fr, rl, rr) wheel speeds, each -1..1
  2. MotorController: turns wheel speeds into GPIO direction pins + PWM duty.
     The GPIO backend is injectable, so tests use a fake and assert the outputs.

Sign convention:
  vy  = forward (+) / reverse (-)
  vx  = strafe right (+) / left (-)
  omega = rotate clockwise / right (+) / left (-)

Hardware: 4-wheel omni base driven by L298N H-bridges (see config.MOTORS) —
one L298N channel per wheel (in1/in2 direction + en PWM speed).
"""
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from . import config

WHEELS = ("FL", "FR", "RL", "RR")


def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))


def buttons_to_velocity(pressed, speed=None):
    """Map pressed PS2 buttons to a (vx, vy, omega) velocity vector.

    D-pad drives translation; L1/R1 rotate. Opposite presses cancel out.
    """
    if speed is None:
        speed = config.DRIVE_SPEED
    vx = vy = omega = 0.0
    if "Up" in pressed:
        vy += 1.0
    if "Down" in pressed:
        vy -= 1.0
    if "Right" in pressed:
        vx += 1.0
    if "Left" in pressed:
        vx -= 1.0
    if "R1" in pressed:
        omega += 1.0
    if "L1" in pressed:
        omega -= 1.0
    return (clamp(vx) * speed, clamp(vy) * speed, clamp(omega) * speed)


def mix(vx, vy, omega):
    """X-drive/mecanum mixing -> (FL, FR, RL, RR), normalised to <= 1.0."""
    fl = vy + vx + omega
    fr = vy - vx - omega
    rl = vy - vx + omega
    rr = vy + vx - omega
    # Scale down together if any wheel exceeds full speed, preserving direction.
    peak = max(1.0, abs(fl), abs(fr), abs(rl), abs(rr))
    return (fl / peak, fr / peak, rl / peak, rr / peak)


class MotorController:
    """Drive the four wheels via H-bridge direction pins + PWM enable pins."""

    def __init__(self, gpio=GPIO, motors=None, pwm_freq=None):
        self.gpio = gpio
        self.motors = motors if motors is not None else config.MOTORS
        self.pwm_freq = pwm_freq if pwm_freq is not None else config.MOTOR_PWM_FREQ
        self._pwm = {}

    def setup(self):
        if self.gpio is None:
            raise RuntimeError("No GPIO backend - run on the Pi or inject one.")
        self.gpio.setmode(self.gpio.BCM)
        for name, spec in self.motors.items():
            self.gpio.setup(spec["in1"], self.gpio.OUT)
            self.gpio.setup(spec["in2"], self.gpio.OUT)
            self.gpio.setup(spec["en"], self.gpio.OUT)
            pwm = self.gpio.PWM(spec["en"], self.pwm_freq)
            pwm.start(0)
            self._pwm[name] = pwm

    def _set_motor(self, name, speed):
        """speed in [-1, 1]: sign = direction, magnitude = PWM duty."""
        spec = self.motors[name]
        speed = clamp(speed)
        if speed > 0:
            self.gpio.output(spec["in1"], self.gpio.HIGH)
            self.gpio.output(spec["in2"], self.gpio.LOW)
        elif speed < 0:
            self.gpio.output(spec["in1"], self.gpio.LOW)
            self.gpio.output(spec["in2"], self.gpio.HIGH)
        else:  # coast/stop
            self.gpio.output(spec["in1"], self.gpio.LOW)
            self.gpio.output(spec["in2"], self.gpio.LOW)
        self._pwm[name].ChangeDutyCycle(abs(speed) * 100.0)

    def set_wheels(self, fl, fr, rl, rr):
        """Apply the four wheel speeds (each -1..1)."""
        for name, speed in zip(WHEELS, (fl, fr, rl, rr)):
            self._set_motor(name, speed)

    def stop(self):
        self.set_wheels(0, 0, 0, 0)

    def cleanup(self):
        self.stop()
        for pwm in self._pwm.values():
            pwm.stop()
        if self.gpio is not None:
            self.gpio.cleanup()


def drive(controller, pressed):
    """High-level: PS2 buttons -> velocity -> wheel mix -> motors."""
    vx, vy, omega = buttons_to_velocity(pressed)
    controller.set_wheels(*mix(vx, vy, omega))
