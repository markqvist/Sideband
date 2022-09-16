import subprocess as sb
from plyer.facades import Orientation


class LinuxOrientation(Orientation):

    def _set_landscape(self, **kwargs):
        self.rotate = 'normal'
        self.screen = sb.check_output(
            "xrandr -q | grep ' connected' |  head -n 1 | cut -d ' ' -f1",
            shell=True
        )
        self.screen = self.screen.decode('utf-8').split('\n')[0]
        sb.call(["xrandr", "--output", self.screen, "--rotate", self.rotate])

    def _set_portrait(self, **kwargs):
        self.rotate = 'left'
        self.screen = sb.check_output(
            "xrandr -q | grep ' connected' |  head -n 1 | cut -d ' ' -f1",
            shell=True
        )
        self.screen = self.screen.decode('utf-8').split('\n')[0]
        sb.call(["xrandr", "--output", self.screen, "--rotate", self.rotate])


def instance():
    return LinuxOrientation()
