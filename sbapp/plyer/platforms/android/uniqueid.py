'''
Module of Android API for plyer.uniqueid.
'''

from jnius import autoclass
from plyer.platforms.android import activity
from plyer.facades import UniqueID

Secure = autoclass('android.provider.Settings$Secure')


class AndroidUniqueID(UniqueID):
    '''
    Implementation of Android uniqueid API.
    '''

    def _get_uid(self):
        return Secure.getString(
            activity.getContentResolver(),
            Secure.ANDROID_ID
        )


def instance():
    '''
    Instance for facade proxy.
    '''
    return AndroidUniqueID()
