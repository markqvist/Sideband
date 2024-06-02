'''
Android Storage Path
--------------------
'''

from plyer.facades import StoragePath
from plyer.platforms.android import SDK_INT
from jnius import autoclass, cast
from android import mActivity

Environment = autoclass("android.os.Environment")
Context = autoclass("android.content.Context")


class AndroidStoragePath(StoragePath):

    def _get_home_dir(self):
        return Environment.getDataDirectory().getAbsolutePath()

    def _get_external_storage_dir(self):
        return Environment.getExternalStorageDirectory().getAbsolutePath()

    def _get_sdcard_dir(self):
        '''
        .. versionadded:: 1.4.0
        '''
        path = None
        context = mActivity.getApplicationContext()
        storage_manager = cast(
            "android.os.storage.StorageManager",
            context.getSystemService(Context.STORAGE_SERVICE),
        )

        if storage_manager is not None:
            if SDK_INT >= 24:
                storage_volumes = storage_manager.getStorageVolumes()
                for storage_volume in storage_volumes:
                    if storage_volume.isRemovable():
                        try:
                            directory = storage_volume.getDirectory()
                        except AttributeError:
                            directory = storage_volume.getPathFile()
                        path = directory.getAbsolutePath()
            else:
                storage_volumes = storage_manager.getVolumeList()
                for storage_volume in storage_volumes:
                    if storage_volume.isRemovable():
                        path = storage_volume.getPath()

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
