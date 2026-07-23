"""Hardware configuration for the flood robot (Raspberry Pi side).

BCM pin numbering. Values taken directly from the working robot scripts so the
individual modules (sensors, motion, camera) share one source of truth.
"""

# === Ultrasonic (HC-SR04) ===
TRIG_PIN = 23
ECHO_PIN = 24

# === Flood-alert LEDs ===
RED = 17
YELLOW = 27
GREEN = 22

# === Passive buzzer (GPIO13) ===
BUZZER_PIN = 13

# === PS2 controller (bit-bang) ===
PS2_CMD = 14      # GPIO14 -> PS2_CMD   (Pi -> controller)
PS2_DATA = 2      # GPIO2  <- PS2_DATA  (controller -> Pi, via voltage divider!)
PS2_CLK = 3       # GPIO3  -> PS2_CLK   (clock)
PS2_ATT = 15      # GPIO15 -> PS2_ATT   (attention / select)
PS2_PAIR = 4      # GPIO4  -> receiver pair/interrupt pin
PS2_ACK = 4       # optional ACK line (alternate bit-bang reader)

# === Video stream (robot -> laptop ground station) ===
STREAM_HOST = "192.168.121.254"   # laptop ground-station IP
STREAM_PORT = 5002                # must match ground_station.config.UDP_PORT
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# === Omni-wheel motors (4-wheel omni, L293D H-bridge) ===
# LongKang Hero uses 4 TT motors + 4 omni wheels driven by 2x L293D drivers.
# Each wheel maps to one L293D channel: in1/in2 = direction, en = enable (PWM
# speed). One L293D drives 2 motors, so 4 wheels = two L293D boards.
#
# NOTE ON HARDWARE: locomotion runs on an Arduino Uno R3 (PS2 controller + the
# two L293D drivers are wired to the Uno; see firmware/arduino/), while the
# Raspberry Pi 5 handles sensing, camera, clearing and app comms. These pins are
# only used by the optional Pi-side driver (motors.MotorController) and are
# placeholders on free GPIOs — set them to your wiring if you drive from the Pi.
MOTORS = {
    "FL": {"in1": 5,  "in2": 6,  "en": 12},   # front-left
    "FR": {"in1": 16, "in2": 19, "en": 18},   # front-right
    "RL": {"in1": 20, "in2": 21, "en": 25},   # rear-left
    "RR": {"in1": 26, "in2": 7,  "en": 8},    # rear-right
}
MOTOR_PWM_FREQ = 1000   # Hz
DRIVE_SPEED = 1.0       # 0..1 scale applied to button-driven motion

# === LED distance thresholds (cm) ===
# Closer water surface = higher flood risk.
RED_THRESHOLD = 100     # <= 100 cm : danger
YELLOW_THRESHOLD = 200  # <= 200 cm : warning
GREEN_THRESHOLD = 300   # <= 300 cm : safe
