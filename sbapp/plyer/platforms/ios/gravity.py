'''
iOS Gravity
-----------

'''

from plyer.facades import Gravity
from pyobjus import autoclass


class iOSGravity(Gravity):

    def __init__(self):
        self.bridge = autoclass('bridge').alloc().init()
        self.bridge.motionManager.setDeviceMotionUpdateInterval_(0.1)

    def _enable(self):
        self.bridge.startDeviceMotion()

    def _disable(self):
        self.bridge.stopDeviceMotion()

    def _get_gravity(self):
        return (
            self.bridge.g_x,
            self.bridge.g_y,
            self.bridge.g_z)


def instance():
    return iOSGravity()
