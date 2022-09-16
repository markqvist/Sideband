'''
MacOSX accelerometer
---------------------
'''

from plyer.facades import Accelerometer
from plyer.platforms.macosx.libs import osx_motion_sensor


class OSXAccelerometer(Accelerometer):
    def _enable(self):
        try:
            osx_motion_sensor.get_coord()
        except Exception:
            raise Exception('Could not enable motion sensor on this macbook!')

    def _disable(self):
        pass

    def _get_acceleration(self):
        return osx_motion_sensor.get_coord()


def instance():
    return OSXAccelerometer()
