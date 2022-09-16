'''
Linux Storage Path
--------------------
'''

from plyer.facades import StoragePath
from os.path import expanduser, dirname, abspath, join, exists

# Default paths for each name
USER_DIRS = "/.config/user-dirs.dirs"

PATHS = {
    "DESKTOP": "Desktop",
    "DOCUMENTS": "Documents",
    "DOWNLOAD": "Downloads",
    "MUSIC": "Music",
    "PICTURES": "Pictures",
    "VIDEOS": "Videos"
}


class LinuxStoragePath(StoragePath):

    def _get_from_user_dirs(self, name):
        home_dir = self._get_home_dir()
        default = join(home_dir, PATHS[name])
        user_dirs = join(home_dir, USER_DIRS)
        if not exists(user_dirs):
            return default

        with open(user_dirs, "r") as f:
            for line in f.readlines():
                if line.startswith("XDG_" + name):
                    return line.split('"')[1]

        return default

    def _get_home_dir(self):
        return expanduser('~')

    def _get_external_storage_dir(self):
        return "/media/" + self._get_home_dir().split("/")[-1]

    def _get_root_dir(self):
        return "/"

    def _get_documents_dir(self):
        directory = self._get_from_user_dirs("DOCUMENTS")
        return directory.replace("$HOME", self._get_home_dir())

    def _get_downloads_dir(self):
        directory = self._get_from_user_dirs("DOWNLOAD")
        return directory.replace("$HOME", self._get_home_dir())

    def _get_videos_dir(self):
        directory = self._get_from_user_dirs("VIDEOS")
        return directory.replace("$HOME", self._get_home_dir())

    def _get_music_dir(self):
        directory = self._get_from_user_dirs("MUSIC")
        return directory.replace("$HOME", self._get_home_dir())

    def _get_pictures_dir(self):
        directory = self._get_from_user_dirs("PICTURES")
        return directory.replace("$HOME", self._get_home_dir())

    def _get_application_dir(self):
        return dirname(abspath(__name__))


def instance():
    return LinuxStoragePath()
