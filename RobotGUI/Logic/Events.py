from RobotGUI.Logic        import Global
from RobotGUI.Logic.Global import printf

class Event:
    def __init__(self):
        self.parameters = {}


class InitEvent(Event):
    def __init__(self, parameters):
        super(InitEvent, self).__init__()
        self.hasBeenRun = False

    def isActive(self, shared):
        # Returns true or false if this event should be activated

        if self.hasBeenRun:
            return False
        else:
            self.hasBeenRun = True
            return True


class DestroyEvent(Event):
    def __init__(self, parameters):
        super(DestroyEvent, self).__init__()

    def isActive(self, shared):
        # This event always returns false, because it is run DIRECTLY by the ControlPanel.programThread()
        # programThread() will check if the event exists. If it does, it will run all of its commands.
        # Otherwise, this event will never run while the program is running.
        return False


class StepEvent(Event):
    def __init__(self, parameters):
        super(StepEvent, self).__init__()

    def isActive(self, shared):
        # Since this is a "step" event, it will run each time the events are checked
        return True


class KeypressEvent(Event):

    def __init__(self, parameters):
        super(KeypressEvent, self).__init__()
        self.parameters = parameters

        # Constants for movement. These are set the first time isActive() is run
        self.low  = None
        self.med  = None
        self.high = None


    def isActive(self, shared):
        if ord(self.parameters["checkKey"]) in Global.keysPressed:
            return True
        else:
            return False


class MotionEvent(Event):
    """
    This event activates when the sensor on the tip of the robots sucker is pressed/triggered
    """

    def __init__(self, parameters):
        super(MotionEvent, self).__init__()
        self.parameters = parameters

        # Constants for movement. These are set the first time isActive() is run
        self.low  = None
        self.med  = None
        self.high = None

    def isActive(self, shared):
        if self.low is None:  # If this is the first time the event is being done, calculate the thresholds
            calib      = shared.getSettings()["motionCalibrations"]
            if calib is None or not ("stationaryMovement" and "activeMovement") in calib:
                printf("MotionEvent.isActive(): ERROR: No movementCalibrations found in order to check motion event")
                return False
            stationary = calib["stationaryMovement"]
            active     = calib["activeMovement"]

            diff  = (active - stationary) / 3
            self.low  = diff
            self.med  = diff * 2
            self.high = diff * 3


        currentMotion = shared.getVision().getMotion()

        active = True

        if self.parameters["low"] == "Low":
            active = active and self.low < currentMotion
        if self.parameters["low"] == "Med":
            active = active and self.med < currentMotion
        if self.parameters["low"] == "High":
            active = active and self.high < currentMotion

        if self.parameters["high"] == "Low":
            active = active and currentMotion < self.low
        if self.parameters["high"] == "Med":
            active = active and currentMotion < self.med
        if self.parameters["high"] == "High":
            active = active and currentMotion < self.high

        return active  #self.parameters["lowThreshold"] < motion < self.parameters["upperThreshold"]


class TipEvent(Event):
    """
    This event activates when the sensor on the tip of the robots sucker is pressed/triggered
    """

    def __init__(self, parameters):
        super(TipEvent, self).__init__()

    def isActive(self, shared):
        return shared.getRobot().getTipSensor()



