'''
iOS Brightness
--------------
'''

from pyobjus import autoclass
from plyer.facades import Brightness
from pyobjus.dylib_manager import load_framework

load_framework('/System/Library/Frameworks/UIKit.framework')
UIScreen = autoclass('UIScreen')


class iOSBrightness(Brightness):

    def __init__(self):
        self.screen = UIScreen.mainScreen()

    def _current_level(self):
        return self.screen.brightness * 100

    def set_level(self, level):
        self.screen.brightness = level / 100


def instance():
    return iOSBrightness()
