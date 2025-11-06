from AbstractDeviceController import AbstractDeviceController
from time import sleep

class DummyDeviceController(AbstractDeviceController):
    def __init__(self):
        self._indicatorStatus = False

    def readSensor(self) -> bool:
        # Simulate package detection - in real implementation, this would read hardware
        return True  # Always detect package for testing

    def setIndicator(self, newState: bool):
        self._indicatorStatus = newState
        print(f"Indicator set to: {newState}")

    def getIndicator(self) -> bool:
        return self._indicatorStatus

    def SendNotification(self):
        print("Sending notification...")
        sleep(1)  # Simulate network delay synchronously
        return True