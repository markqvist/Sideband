'''
Module of Windows API helper for plyer.battery.
'''

__all__ = ('battery_status')


import ctypes
from plyer.platforms.win.libs import win_api_defs


def battery_status():
    '''
    Implementation of Windows system power status API for plyer.battery.
    '''

    status = win_api_defs.SYSTEM_POWER_STATUS()
    if not win_api_defs.GetSystemPowerStatus(ctypes.pointer(status)):
        raise Exception('Could not get system power status.')

    return dict(
        (field, getattr(status, field))
        for field, _ in status._fields_
    )
