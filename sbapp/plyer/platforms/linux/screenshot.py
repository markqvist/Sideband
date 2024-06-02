import subprocess
from os.path import join
from sbapp.plyer.facades import Screenshot
from sbapp.plyer.utils import whereis_exe
from sbapp.plyer.platforms.linux.storagepath import LinuxStoragePath


class LinuxScreenshot(Screenshot):
    def __init__(self, file_path=None):
        default_path = join(
            LinuxStoragePath().get_pictures_dir(),
            'screenshot.xwd'
        )
        super().__init__(file_path or default_path)

    def _capture(self):
        # call xwd and redirect bytes from stdout to file
        with open(self.file_path, 'wb') as fle:
            subprocess.call([
                # quiet, full screen root window
                'xwd', '-silent', '-root',
            ], stdout=fle)


def instance():
    if whereis_exe('xwd'):
        return LinuxScreenshot()
    else:
        return Screenshot()
