'''
Module of Win API for plyer.devicename.
'''

import socket
from plyer.facades import DeviceName


class WinDeviceName(DeviceName):
    '''
    Implementation of Linux DeviceName API.
    '''

    def _get_device_name(self):
        hostname = socket.gethostname()
        return hostname


def instance():
    '''
    Instance for facade proxy.
    '''
    return WinDeviceName()
