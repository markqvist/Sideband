'''Implementation Vibrator for iOS.

Install: Add AudioToolbox framework to your application.
'''

import ctypes
from plyer.facades import Vibrator


class IosVibrator(Vibrator):
    '''iOS Vibrator class.

    iOS doesn't support any feature.
    All time, pattern, repetition are ignored.
    '''

    def __init__(self):
        super().__init__()
        try:
            self._func = ctypes.CDLL(None).AudioServicesPlaySystemSound
        except AttributeError:
            self._func = None

    def _vibrate(self, time=None, **kwargs):
        # kSystemSoundID_Vibrate is 0x00000FFF
        self._func(0xFFF)

    def _pattern(self, pattern=None, repeat=None, **kwargs):
        self._vibrate()

    def _exists(self, **kwargs):
        return self._func is not None

    def _cancel(self, **kwargs):
        pass


def instance():
    '''Returns Vibrator

    :return: instance of class IosVibrator
    '''
    return IosVibrator()
