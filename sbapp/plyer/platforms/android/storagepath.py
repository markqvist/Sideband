'''
Android Storage Path
--------------------
'''

from os import listdir, access, R_OK
from os.path import join
from plyer.facades import StoragePath
from jnius import autoclass
from android import mActivity

Environment = autoclass('android.os.Environment')
Context = autoclass('android.content.Context')


class AndroidStoragePath(StoragePath):

    def _get_home_dir(self):
        return Environment.getDataDirectory().getAbsolutePath()

    def _get_external_storage_dir(self):
        return Environment.getExternalStorageDirectory().getAbsolutePath()

    def _get_sdcard_dir(self):
        '''
        .. versionadded:: 1.4.0
        '''
        # folder in /storage/ that is readable
        # and is not internal SD card
        path = None
        for folder in listdir('/storage'):
            folder = join('/storage', folder)
            if folder in self._get_external_storage_dir():
                continue
            if not access(folder, R_OK):
                continue
            path = folder
            break
        return path

    def _get_root_dir(self):
        return Environment.getRootDirectory().getAbsolutePath()

    def _get_documents_dir(self):
        return Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOCUMENTS).getAbsolutePath()

    def _get_downloads_dir(self):
        return Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()

    def _get_videos_dir(self):
        return Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_MOVIES).getAbsolutePath()

    def _get_music_dir(self):
        return Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_MUSIC).getAbsolutePath()

    def _get_pictures_dir(self):
        return Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_PICTURES).getAbsolutePath()

    def _get_application_dir(self):
        return mActivity.getFilesDir().getParentFile().getParent()


def instance():
    return AndroidStoragePath()
