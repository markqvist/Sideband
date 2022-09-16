'''
Module of MacOSX API for plyer.devicename.
'''

import socket
from plyer.facades import DeviceName


class OSXDeviceName(DeviceName):
    '''
    Implementation of MacOSX DeviceName API.
    '''

    def _get_device_name(self):
        hostname = socket.gethostname()
        return hostname


def instance():
    '''
    Instance for facade proxy.
    '''
    return OSXDeviceName()
