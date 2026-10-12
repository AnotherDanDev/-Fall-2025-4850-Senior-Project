# Smart Mailbox Package Detector

![Smart mailbox package detector](mailbox.jpg)

A Raspberry Pi package detector built for the CS 4850 Senior Project (Fall 2025). An infrared beam inside the box detects when a package is sitting in it. When one arrives, the Pi raises a servo-driven flag and sends a Telegram message. When the package is removed, the flag lowers again.

▶️ **[Watch it in action on YouTube](https://youtu.be/JGV6e0Mno3Q)**

## How it works

An IR LED sends short 38 kHz bursts at a demodulating IR receiver. With the box empty, the receiver picks up the bursts. When a package blocks the beam, the bursts are missed.

Every check cycle, `InBoxTest.py`:

1. Sends 10 bursts of 38 kHz IR (560 µs each, 33.3% duty cycle) using pigpio hardware PWM.
2. Watches the receiver for 15 ms after each burst and counts hits and misses.
3. Decides a package is present if 7 or more of the 10 bursts were missed.
4. If that result changed since the last check, moves the servo to raise or lower the flag, and sends a Telegram message when a package arrives.
5. Waits 5 seconds and repeats.

Requiring most of the bursts to be missed means one bad reading doesn't flip the result. Acting only when the result changes means you get one message per delivery instead of one every five seconds.

## Hardware

| Part | Connection (BCM numbering) |
|---|---|
| IR LED | GPIO 18 (hardware PWM) |
| Demodulating IR receiver, active-low | GPIO 21, internal pull-up enabled |
| Servo that raises and lowers the flag | GPIO 26 |
| Raspberry Pi running the `pigpio` daemon | — |

The IR LED has to be on a pin that supports hardware PWM (12, 13, 18 or 19).

## Tuning

These constants are at the top of `InBoxTest.py`:

| Setting | Default | Purpose |
|---|---|---|
| `CHECK_INTERVAL_SEC` | 5.0 | Time between checks |
| `CARRIER_HZ` | 38000 | IR carrier frequency; match your receiver |
| `BURST_US` | 560 | Length of each burst |
| `DUTY_PCT` | 33.3 | Carrier duty cycle |
| `BURSTS_PER_CHECK` | 10 | Bursts per check |
| `DETECT_WINDOW_MS` | 15 | How long to listen after each burst |
| `THRESHOLD_MISSES` | 7 | Misses needed to count as "package present" |
| `SENSOR_ACTIVE_LOW` | True | Receiver output polarity |
| `FLAG_UP_DEG` / `FLAG_DN_DEG` | 180 / 90 | Servo angles for flag up and flag down |
| `SERVO_MIN_US` / `SERVO_MAX_US` | 500 / 2500 | Servo pulse widths for 0° and 180° |
| `MOVE_PAUSE_S` | 0.4 | Time allowed for the servo to finish moving |

`THRESHOLD_MISSES` is compared against `BURSTS_PER_CHECK`, so if you change one, adjust the other to keep the same ratio.

## Repository layout

| File | Description |
|---|---|
| `InBoxTest.py` | The main program: IR beam check, servo flag and Telegram alert |
| `burst.py` | IR LED test. Loops an NEC-style pattern of 38 kHz bursts (560 µs on, 1680 µs off) on GPIO 18 |
| `servotest.py` | Standalone servo test, separate from the sensor. Centers the servo, sweeps it 0°→180°→0° in 10° steps, then re-centers. Uses GPIO 16. For testing the flag. |
| `test.py` | Turns the IR LED (GPIO 12) on and off with a physical switch (GPIO 17) using `gpiozero` |
| `AbstractDeviceController.py` | Abstract interface for the hardware: read the sensor, set and get the indicator LED, send a notification |
| `DummyDeviceController.py` | Simulated controller for running without hardware. Its sensor always reports a package |
| `MailDetector.py` | State-machine version of the detector (await package → send notification → wait for removal) built on the controller interface |

`MailDetector.py` only runs with the dummy controller. Running it with Python's `-O` flag raises an exception because no hardware controller is implemented. `InBoxTest.py` is the version that runs on the hardware.
