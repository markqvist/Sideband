'''
iOS Compass
-----------
'''

from plyer.facades import Compass
from pyobjus import autoclass


class IosCompass(Compass):

    def __init__(self):
        super().__init__()
        self.bridge = autoclass('bridge').alloc().init()
        self.bridge.motionManager.setMagnetometerUpdateInterval_(0.1)
        self.bridge.motionManager.setDeviceMotionUpdateInterval_(0.1)

    def _enable(self):
        self.bridge.startMagnetometer()
        self.bridge.startDeviceMotionWithReferenceFrame()

    def _disable(self):
        self.bridge.stopMagnetometer()
        self.bridge.stopDeviceMotion()

    def _get_orientation(self):
        return (
            self.bridge.mf_x,
            self.bridge.mf_y,
            self.bridge.mf_z)

    def _get_field_uncalib(self):
        return (
            self.bridge.mg_x,
            self.bridge.mg_y,
            self.bridge.mg_z,
            self.bridge.mg_x - self.bridge.mf_x,
            self.bridge.mg_y - self.bridge.mf_y,
            self.bridge.mg_z - self.bridge.mf_z)


def instance():
    return IosCompass()
