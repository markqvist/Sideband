'''
Linux Brightness
----------------

'''

from plyer.facades import Brightness
import subprocess
import os


class LinuxBrightness(Brightness):

    def __init__(self):
        if os.system("which xbacklight"):
            msg = ("It looks like 'xbacklight' is not installed. Try "
                   "installing it with your distribution's package manager.")
            raise Exception(msg)

    def _current_level(self):
        cr_level = subprocess.check_output(["xbacklight", "-get"])
        return str(cr_level)

    def _set_level(self, level):
        subprocess.call(["xbacklight", "-set", str(level)])


def instance():
    return LinuxBrightness()
