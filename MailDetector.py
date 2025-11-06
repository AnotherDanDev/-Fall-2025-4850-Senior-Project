from enum import Enum
from time import sleep
import DummyDeviceController

class State(Enum):
    Error = 0
    AwaitPackage = 1
    SendingNotification = 2
    NotificationSent = 3

class MailDetector:
    def __init__(self):
        self._state = State.AwaitPackage
        # Initialize device controller
        if __debug__:
            self._deviceController = DummyDeviceController.DummyDeviceController()
        else:
            raise Exception("Build not implemented please execute in debug.")

    def main(self):
        while self._state != State.Error:
            if self._state == State.AwaitPackage:
                self._handle_await_package()
            elif self._state == State.SendingNotification:
                self._handle_sending_notification()
            elif self._state == State.NotificationSent:
                self._handle_notification_sent()

            sleep(0.1)

    def _handle_await_package(self):
        # Handle state when waiting for a package to be detected
        if self._deviceController.readSensor():
            print("Package detected! Transitioning to SendingNotification")
            self._state = State.SendingNotification
            self._deviceController.setIndicator(True)

    def _handle_sending_notification(self):
        # Handle state when sending notification to user
        self._deviceController.SendNotification()  # Synchronous call
        print("Notification sent successfully! Transitioning to NotificationSent")
        self._state = State.NotificationSent

    def _handle_notification_sent(self):
        # Handle state after notification is sent, waiting for package removal
        if not self._deviceController.readSensor():
            print("Package removed! Transitioning to AwaitPackage")
            self._state = State.AwaitPackage
            self._deviceController.setIndicator(False)

if __name__ == "__main__":
    detector = MailDetector()
    detector.main()