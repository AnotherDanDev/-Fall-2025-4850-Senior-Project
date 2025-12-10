import time, sys, pigpio, requests

# ===== Tunables =====
CHECK_INTERVAL_SEC   = 5.0       # how often to run a check
CARRIER_HZ           = 38000     # IR carrier frequency
BURST_US             = 560       # burst length (microseconds)
DUTY_PCT             = 33.3      # carrier duty cycle (%)
BURSTS_PER_CHECK     = 10        # bursts per check cycle
DETECT_WINDOW_MS     = 15        # watch window after each burst
SENSOR_ACTIVE_LOW    = True      # most demodulating receivers are active-low
THRESHOLD_MISSES     = 7         # If the sensor misses above this many bursts then we have a package (convert into percentile?)
MSG = "📦 Package detected!"
BOT_TOKEN = "8513702387:AAHqH1mpvITBQ5OooT4PLLWKK6bRSU-EKPw"
CHAT_ID = "6286980692"


# Servo (flag) settings
SERVO_GPIO   = 26    
SERVO_MIN_US = 500   
SERVO_MAX_US = 2500     
FLAG_UP_DEG  = 180    # angle when package detected (raise flag)
FLAG_DN_DEG  = 90     # angle when clear (lower flag)
MOVE_PAUSE_S = 0.4   
# ====================

LED_GPIO = 18
RX_GPIO  = 21

def pulse_for_angle(angle_deg: float) -> int:
    angle_deg = max(0.0, min(180.0, float(angle_deg)))
    span = SERVO_MAX_US - SERVO_MIN_US
    return int(SERVO_MIN_US + (span * (angle_deg / 180.0)))

def now_ms():
    return time.time() * 1000.0

def send_burst(pi):
    pi.hardware_PWM(LED_GPIO, CARRIER_HZ, int(DUTY_PCT * 10000))  # duty in millionths
    time.sleep(BURST_US / 1_000_000.0)
    pi.hardware_PWM(LED_GPIO, 0, 0)

def saw_pulse(pi, window_ms):
    deadline = now_ms() + window_ms
    while now_ms() < deadline:
        val = pi.read(RX_GPIO)
        active = (val == 0) if SENSOR_ACTIVE_LOW else (val == 1)
        if active:
            return True
    return False

def set_flag(pi, up: bool):
    target_deg = FLAG_UP_DEG if up else FLAG_DN_DEG
    pi.set_servo_pulsewidth(SERVO_GPIO, pulse_for_angle(target_deg))
    time.sleep(MOVE_PAUSE_S)

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("ERROR: pigpio daemon not running. Start it with: sudo pigpiod", file=sys.stderr)
        sys.exit(1)

    try:
        # Sensor input (pull-up for active-low; pull-down for active-high)
        pi.set_mode(RX_GPIO, pigpio.INPUT)
        pi.set_pull_up_down(RX_GPIO, pigpio.PUD_UP if SENSOR_ACTIVE_LOW else pigpio.PUD_DOWN)

        # Initialize servo to DOWN
        set_flag(pi, up=False)

        print(f"IR+Servo checker every {CHECK_INTERVAL_SEC}s; threshold {THRESHOLD_MISSES}/{BURSTS_PER_CHECK} misses.")

        last_package = None
        while True:
            misses = 0
            hits   = 0
            for _ in range(BURSTS_PER_CHECK):
                send_burst(pi)
                detected = saw_pulse(pi, DETECT_WINDOW_MS)
                if detected:
                    hits += 1
                else:
                    misses += 1
                time.sleep(0.005)  # spacing between bursts

            package = (misses >= THRESHOLD_MISSES)

            if last_package is None or package != last_package:
                if package:
                    print("Sending message")
                    requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": CHAT_ID, "text": MSG}, timeout=5
                    )


            # Only move the servo when the state changes
            if last_package is None or package != last_package:
                set_flag(pi, up=package)

            print(f"[{time.strftime('%H:%M:%S')}] hits={hits} misses={misses}  -> "
                  f"{'PACKAGE DETECTED (flag UP)' if package else 'clear (flag DOWN)'}")

            last_package = package
            time.sleep(CHECK_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        try:
            pi.hardware_PWM(LED_GPIO, 0, 0)
        except Exception:
            pass
        # Stop servo pulses so it doesn’t buzz or draw idle current
        try:
            pi.set_servo_pulsewidth(SERVO_GPIO, 0)
        except Exception:
            pass
        pi.stop()

if __name__ == "__main__":
    main()
