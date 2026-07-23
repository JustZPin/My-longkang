"""Tests for PS2 -> motion control (robot/motors.py).

Pure logic + a fake GPIO backend, so the whole motion path is verified with no
Raspberry Pi and no motors attached.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from robot import motors  # noqa: E402
from robot.motors import MotorController, buttons_to_velocity, mix  # noqa: E402


# --- pure velocity mapping -------------------------------------------------

def test_no_buttons_is_stationary():
    assert buttons_to_velocity([]) == (0.0, 0.0, 0.0)


def test_forward_and_reverse():
    assert buttons_to_velocity(["Up"]) == (0.0, 1.0, 0.0)
    assert buttons_to_velocity(["Down"]) == (0.0, -1.0, 0.0)


def test_strafe_and_rotate():
    assert buttons_to_velocity(["Right"]) == (1.0, 0.0, 0.0)
    assert buttons_to_velocity(["Left"]) == (-1.0, 0.0, 0.0)
    assert buttons_to_velocity(["R1"]) == (0.0, 0.0, 1.0)   # rotate right
    assert buttons_to_velocity(["L1"]) == (0.0, 0.0, -1.0)  # rotate left


def test_opposite_buttons_cancel():
    assert buttons_to_velocity(["Up", "Down"]) == (0.0, 0.0, 0.0)


def test_speed_scaling():
    assert buttons_to_velocity(["Up"], speed=0.5) == (0.0, 0.5, 0.0)


# --- wheel mixing ----------------------------------------------------------

def test_mix_forward_drives_all_wheels_equally():
    assert mix(0, 1, 0) == (1.0, 1.0, 1.0, 1.0)


def test_mix_strafe_right_pattern():
    # FL fwd, FR back, RL back, RR fwd
    assert mix(1, 0, 0) == (1.0, -1.0, -1.0, 1.0)


def test_mix_rotate_right_pattern():
    # left wheels fwd, right wheels back
    assert mix(0, 0, 1) == (1.0, -1.0, 1.0, -1.0)


def test_mix_is_normalised():
    # Diagonal would exceed 1.0 before normalising.
    fl, fr, rl, rr = mix(1, 1, 0)
    assert max(abs(fl), abs(fr), abs(rl), abs(rr)) <= 1.0
    assert (fl, fr, rl, rr) == (1.0, 0.0, 0.0, 1.0)


# --- MotorController with a fake GPIO --------------------------------------

class FakePWM:
    def __init__(self, pin, freq):
        self.pin, self.freq, self.duty, self.running = pin, freq, 0.0, False

    def start(self, duty):
        self.running, self.duty = True, duty

    def ChangeDutyCycle(self, duty):
        self.duty = duty

    def ChangeFrequency(self, freq):
        self.freq = freq

    def stop(self):
        self.running = False


class FakeGPIO:
    BCM, OUT, IN, HIGH, LOW = "BCM", "OUT", "IN", 1, 0

    def __init__(self):
        self.mode = None
        self.pin_state = {}
        self.pwms = {}

    def setmode(self, mode):
        self.mode = mode

    def setup(self, pin, direction, **kwargs):
        self.pin_state.setdefault(pin, None)

    def output(self, pin, value):
        self.pin_state[pin] = value

    def PWM(self, pin, freq):
        pwm = FakePWM(pin, freq)
        self.pwms[pin] = pwm
        return pwm

    def cleanup(self):
        pass


def _make_controller():
    gpio = FakeGPIO()
    ctl = MotorController(gpio=gpio)
    ctl.setup()
    return gpio, ctl


def test_setup_starts_a_pwm_per_wheel():
    gpio, ctl = _make_controller()
    assert len(gpio.pwms) == 4
    assert gpio.mode == FakeGPIO.BCM


def test_forward_sets_all_wheels_forward_full_duty():
    gpio, ctl = _make_controller()
    ctl.set_wheels(1, 1, 1, 1)
    for spec in ctl.motors.values():
        assert gpio.pin_state[spec["in1"]] == FakeGPIO.HIGH
        assert gpio.pin_state[spec["in2"]] == FakeGPIO.LOW
        assert gpio.pwms[spec["en"]].duty == 100.0


def test_reverse_flips_direction_pins():
    gpio, ctl = _make_controller()
    ctl.set_wheels(-1, -1, -1, -1)
    for spec in ctl.motors.values():
        assert gpio.pin_state[spec["in1"]] == FakeGPIO.LOW
        assert gpio.pin_state[spec["in2"]] == FakeGPIO.HIGH


def test_stop_zeroes_duty_and_pins():
    gpio, ctl = _make_controller()
    ctl.set_wheels(1, 1, 1, 1)
    ctl.stop()
    for spec in ctl.motors.values():
        assert gpio.pin_state[spec["in1"]] == FakeGPIO.LOW
        assert gpio.pin_state[spec["in2"]] == FakeGPIO.LOW
        assert gpio.pwms[spec["en"]].duty == 0.0


def test_drive_forward_end_to_end():
    # Pressing "Up" should move all four wheels forward at full duty.
    gpio, ctl = _make_controller()
    motors.drive(ctl, ["Up"])
    for spec in ctl.motors.values():
        assert gpio.pin_state[spec["in1"]] == FakeGPIO.HIGH
        assert gpio.pwms[spec["en"]].duty == 100.0
