import subprocess
from os.path import join
from sbapp.plyer.facades import Screenshot
from sbapp.plyer.utils import whereis_exe
from sbapp.plyer.platforms.macosx.storagepath import OSXStoragePath


class OSXScreenshot(Screenshot):
    def __init__(self, file_path=None):
        default_path = join(
            OSXStoragePath().get_pictures_dir().replace('file://', ''),
            'screenshot.png'
        )
        super().__init__(file_path or default_path)

    def _capture(self):
        subprocess.call([
            'screencapture',
            self.file_path
        ])


def instance():
    if whereis_exe('screencapture'):
        return OSXScreenshot()
    else:
        return Screenshot()
