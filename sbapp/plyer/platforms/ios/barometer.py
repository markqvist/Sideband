'''
iOS Barometer
-------------
'''

from plyer.facades import Barometer
from pyobjus import autoclass


class iOSBarometer(Barometer):

    def __init__(self):
        super().__init__()
        self.bridge = autoclass('bridge').alloc().init()

    def _enable(self):
        self.bridge.startRelativeAltitude()

    def _disable(self):
        self.bridge.stopRelativeAltitude()

    def _get_pressure(self):
        '''
        1 kPa = 10 hPa
        '''
        return (
            self.bridge.pressure * 10)


def instance():
    return iOSBarometer()
