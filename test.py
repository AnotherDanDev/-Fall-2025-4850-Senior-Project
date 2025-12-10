#!/usr/bin/env python3
from gpiozero import LED, Button
from signal import pause
from datetime import datetime

IR_PIN = 12   # BCM numbering
SW_PIN = 17   # Switch to GND, uses internal pull-up

ir = LED(IR_PIN)
sw = Button(SW_PIN, pull_up=True, bounce_time=0.05)

def ts():
    return datetime.now().strftime("%H:%M:%S")

def handle_press():
    ir.on()
    print(f"[{ts()}] Switch PRESSED (closed to GND) -> IR ON", flush=True)

def handle_release():
    ir.off()
    print(f"[{ts()}] Switch RELEASED (open) -> IR OFF", flush=True)

# Follow the switch: closed -> IR ON, open -> IR OFF
sw.when_pressed = handle_press
sw.when_released = handle_release

print("Running. Flip the switch to control the IR LED.")
pause()
