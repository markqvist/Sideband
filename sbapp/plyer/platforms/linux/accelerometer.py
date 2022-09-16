'''
Linux accelerometer
---------------------
'''

from plyer.facades import Accelerometer
import glob
import re


class LinuxAccelerometer(Accelerometer):

    def _enable(self):
        pass

    def _disable(self):
        pass

    def _get_acceleration(self):
        try:
            pos = glob.glob("/sys/devices/platform/*/position")[0]
        except IndexError:
            raise Exception('Could not enable accelerometer!')

        with open(pos, "r") as p:
            t = p.read()
            coords = re.findall(r"[-]?\d+\.?\d*", t)
            # Apparently the acceleration on sysfs goes from -1000 to 1000.
            # I divide it by 100 to make it equivalent to Android.
            # The negative is because the coordinates are inverted on Linux
            return [float(i) / -100 for i in coords]


def instance():
    return LinuxAccelerometer()
