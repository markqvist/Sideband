'''
iOS Spatial Orientation
-----------------------

'''

from plyer.facades import SpatialOrientation
from pyobjus import autoclass


class iOSSpatialOrientation(SpatialOrientation):

    def __init__(self):
        self.bridge = autoclass('bridge').alloc().init()
        self.bridge.motionManager.setDeviceMotionUpdateInterval_(0.1)

    def _enable_listener(self):
        self.bridge.startDeviceMotion()

    def _disable_listener(self):
        self.bridge.stopDeviceMotion()

    def _get_orientation(self):
        return (
            self.bridge.sp_yaw,
            self.bridge.sp_pitch,
            self.bridge.sp_roll)


def instance():
    return iOSSpatialOrientation()
