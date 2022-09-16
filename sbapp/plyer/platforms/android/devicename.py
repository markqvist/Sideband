'''
Module of Android API for plyer.devicename.
'''

from jnius import autoclass
from plyer.facades import DeviceName

Build = autoclass('android.os.Build')


class AndroidDeviceName(DeviceName):
    '''
    Implementation of Android devicename API.
    '''

    def _get_device_name(self):
        """
        Method to get the device name aka model in an android environment.

        Changed the implementation from 'android.provider.Settings.Global' to
        'android.os.Build' because 'android.provider.Settings.Global' was
        introduced in API 17 whereas 'android.os.Build' is present since API 1

        Thereby making this method more backward compatible.
        """
        return Build.MODEL


def instance():
    '''
    Instance for facade proxy.
    '''
    return AndroidDeviceName()
