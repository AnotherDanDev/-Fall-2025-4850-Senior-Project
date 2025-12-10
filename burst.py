#!/usr/bin/env python3
# burst_loop_hw_pwm.py
import time, pigpio

PIN = 18            # BCM pin (must be 12/13/18/19 for hardware_PWM)
CARRIER = 38000     # Hz
DUTY = 333333       # 33.333% (in millionths)

pi = pigpio.pi()
assert pi.connected, "Start the daemon first: sudo pigpiod -g"

def mark(us):
    pi.hardware_PWM(PIN, CARRIER, DUTY)
    time.sleep(us / 1_000_000)

def space(us):
    pi.hardware_PWM(PIN, 0, 0)
    time.sleep(us / 1_000_000)

try:
    while True:
        # Example: NEC-like data section: 32 x (560µs mark, 1680µs space)
        for _ in range(32):
            mark(560)
            space(1680)
        time.sleep(0.1)  # small gap between frames
finally:
    pi.hardware_PWM(PIN, 0, 0)
    pi.stop()
