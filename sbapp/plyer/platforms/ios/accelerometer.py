'''
iOS accelerometer
-----------------

Taken from: http://pyobjus.readthedocs.org/en/latest/pyobjus_ios.html \
            #accessing-accelerometer
'''

from plyer.facades import Accelerometer
from pyobjus import autoclass


class IosAccelerometer(Accelerometer):

    def __init__(self):
        super().__init__()
        self.bridge = autoclass('bridge').alloc().init()
        self.bridge.motionManager.setAccelerometerUpdateInterval_(0.1)

    def _enable(self):
        self.bridge.startAccelerometer()

    def _disable(self):
        self.bridge.stopAccelerometer()

    def _get_acceleration(self):
        return (
            self.bridge.ac_x,
            self.bridge.ac_y,
            self.bridge.ac_z)


def instance():
    return IosAccelerometer()
