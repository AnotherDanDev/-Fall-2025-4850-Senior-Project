import abc

class AbstractDeviceController(abc.ABC):

    # Outputs true if the IR sensor is obstructed.
    @abc.abstractmethod
    def readSensor(self) -> bool:
        pass

    # Controls the LED indicator light on the box.
    # True turns on the light and false turns off the light.
    @abc.abstractmethod
    def setIndicator(self, newState: bool):
        pass

    # Returns the state of the LED indicator.
    @abc.abstractmethod
    def getIndicator(self) -> bool:
        pass

    # Sends a notification that a package is detected.
    @abc.abstractmethod
    def SendNotification(self):
        pass