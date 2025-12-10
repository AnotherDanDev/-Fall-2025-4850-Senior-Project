#!/usr/bin/env python3
# servo_test.py — quick SG90 test using pigpio
import time, sys, pigpio

SERVO_GPIO   = 16    # BCM
SERVO_MIN_US = 500   # adjust if needed (typical ~500–600)
SERVO_MAX_US = 2500  # adjust if needed (typical ~2400–2500)
MID_US       = (SERVO_MIN_US + SERVO_MAX_US)//2

def pulse_for_angle(angle_deg: float) -> int:
    angle_deg = max(0.0, min(180.0, float(angle_deg)))
    span = SERVO_MAX_US - SERVO_MIN_US
    return int(SERVO_MIN_US + (span * (angle_deg / 180.0)))

pi = pigpio.pi()
if not pi.connected:
    print("ERROR: pigpio daemon not running. Start with: sudo pigpiod", file=sys.stderr)
    sys.exit(1)

try:
    print("Centering...")
    pi.set_servo_pulsewidth(SERVO_GPIO, MID_US)
    time.sleep(1.0)

    print("Sweep 0° → 180°")
    for a in range(0, 181, 10):
        pi.set_servo_pulsewidth(SERVO_GPIO, pulse_for_angle(a))
        time.sleep(0.15)

    print("Sweep 180° → 0°")
    for a in range(180, -1, -10):
        pi.set_servo_pulsewidth(SERVO_GPIO, pulse_for_angle(a))
        time.sleep(0.15)

    print("Done. Holding at center for 1s…")
    pi.set_servo_pulsewidth(SERVO_GPIO, MID_US)
    time.sleep(1.0)

except KeyboardInterrupt:
    pass
finally:
    # Important: stop pulses to let the servo relax
    pi.set_servo_pulsewidth(SERVO_GPIO, 0)
    pi.stop()
