/*
 * LongKang Hero - locomotion firmware (Arduino Uno R3)
 * -----------------------------------------------------
 * Reads a PS2 wireless controller and drives 4 omni wheels through two L293D
 * H-bridge drivers (one L293D channel per wheel: 2 direction pins + 1 PWM
 * enable pin).
 *
 * This mirrors the omni-wheel mixing that is unit-tested in Python
 * (src/robot/motors.py :: buttons_to_velocity + mix). Keep the two in sync.
 *
 *   vy    = forward (+) / reverse (-)      D-pad Up / Down
 *   vx    = strafe right (+) / left (-)    D-pad Right / Left
 *   omega = rotate right (+) / left (-)    R1 / L1
 *
 *   FL = vy + vx + omega
 *   FR = vy - vx - omega
 *   RL = vy - vx + omega
 *   RR = vy + vx - omega        (all normalised so |speed| <= 1)
 *
 * Requires the PS2X library by Bill Porter ("PS2X_lib").
 */
#include <PS2X_lib.h>

// ---- PS2 controller pins (to the receiver) ----
#define PS2_DAT 12
#define PS2_CMD 11
#define PS2_SEL 10
#define PS2_CLK 13

// ---- Motor pins: {in1, in2, enable(PWM)} per wheel ----
struct Motor { uint8_t in1, in2, en; };
// Enable pins must be PWM-capable (Uno: 3,5,6,9 are free with PS2 on 10-13).
Motor FL = { 2,  4,  3};   // front-left   (L293D #1)
Motor FR = { 7,  8,  5};   // front-right  (L293D #1)
Motor RL = {A0, A1,  6};   // rear-left    (L293D #2)
Motor RR = {A2, A3,  9};   // rear-right   (L293D #2)

PS2X ps2x;

void setupMotor(const Motor &m) {
  pinMode(m.in1, OUTPUT);
  pinMode(m.in2, OUTPUT);
  pinMode(m.en,  OUTPUT);
}

// speed in [-1.0, 1.0]: sign = direction, magnitude = PWM duty.
void driveMotor(const Motor &m, float speed) {
  if (speed > 0.01f) {
    digitalWrite(m.in1, HIGH);
    digitalWrite(m.in2, LOW);
  } else if (speed < -0.01f) {
    digitalWrite(m.in1, LOW);
    digitalWrite(m.in2, HIGH);
  } else {                       // coast / stop
    digitalWrite(m.in1, LOW);
    digitalWrite(m.in2, LOW);
  }
  analogWrite(m.en, (int)(fabs(speed) * 255.0f));
}

void setup() {
  setupMotor(FL); setupMotor(FR); setupMotor(RL); setupMotor(RR);

  // config_gamepad(clk, cmd, att, dat, pressures?, rumble?)
  int err = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, false, false);
  Serial.begin(57600);
  if (err == 0) Serial.println("PS2 controller ready.");
  else          Serial.println("PS2 controller not found - check wiring.");
}

void loop() {
  ps2x.read_gamepad(false, 0);

  // Buttons -> velocity vector (held buttons; opposite presses cancel).
  float vx = 0, vy = 0, omega = 0;
  if (ps2x.Button(PSB_PAD_UP))    vy += 1;
  if (ps2x.Button(PSB_PAD_DOWN))  vy -= 1;
  if (ps2x.Button(PSB_PAD_RIGHT)) vx += 1;
  if (ps2x.Button(PSB_PAD_LEFT))  vx -= 1;
  if (ps2x.Button(PSB_R1))        omega += 1;
  if (ps2x.Button(PSB_L1))        omega -= 1;

  // Omni-wheel mixing (matches motors.mix()).
  float fl = vy + vx + omega;
  float fr = vy - vx - omega;
  float rl = vy - vx + omega;
  float rr = vy + vx - omega;

  // Normalise together so no wheel exceeds full speed.
  float peak = 1.0f;
  peak = max(peak, fabs(fl)); peak = max(peak, fabs(fr));
  peak = max(peak, fabs(rl)); peak = max(peak, fabs(rr));
  fl /= peak; fr /= peak; rl /= peak; rr /= peak;

  driveMotor(FL, fl);
  driveMotor(FR, fr);
  driveMotor(RL, rl);
  driveMotor(RR, rr);

  delay(20);   // ~50 Hz control loop
}
