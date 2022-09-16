'''
iOS Gyroscope
---------------------
'''

from plyer.facades import Gyroscope
from pyobjus import autoclass

from pyobjus.dylib_manager import load_framework

load_framework('/System/Library/Frameworks/UIKit.framework')
UIDevice = autoclass('UIDevice')

device = UIDevice.currentDevice()


class IosGyroscope(Gyroscope):

    def __init__(self):
        super().__init__()
        self.bridge = autoclass('bridge').alloc().init()

        if int(device.systemVersion.UTF8String().split('.')[0]) <= 4:
            self.bridge.motionManager.setGyroscopeUpdateInterval_(0.1)
        else:
            self.bridge.motionManager.setGyroUpdateInterval_(0.1)

        self.bridge.motionManager.setDeviceMotionUpdateInterval_(0.1)

    def _enable(self):
        self.bridge.startGyroscope()
        self.bridge.startDeviceMotion()

    def _disable(self):
        self.bridge.stopGyroscope()
        self.bridge.stopDeviceMotion()

    def _get_orientation(self):
        return (
            self.bridge.rotation_rate_x,
            self.bridge.rotation_rate_y,
            self.bridge.rotation_rate_z)

    def _get_rotation_uncalib(self):
        return (
            self.bridge.gy_x,
            self.bridge.gy_y,
            self.bridge.gy_z,
            self.bridge.gy_x - self.bridge.rotation_rate_x,
            self.bridge.gy_y - self.bridge.rotation_rate_y,
            self.bridge.gy_z - self.bridge.rotation_rate_z)


def instance():
    return IosGyroscope()
