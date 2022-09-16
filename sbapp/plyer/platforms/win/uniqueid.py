'''
Module of Windows API for plyer.uniqueid.
'''

try:
    import _winreg as regedit
except ImportError:
    try:
        import winreg as regedit
    except ImportError:
        raise NotImplementedError()

from plyer.facades import UniqueID


class WinUniqueID(UniqueID):
    '''
    Implementation of Windows battery API.
    '''

    def _get_uid(self):
        # Win XP+, REG QUERY KEY /V VALUE, case-insensitive
        handle = regedit.OpenKey(
            regedit.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\\Microsoft\\Cryptography", 0,
            regedit.KEY_READ | regedit.KEY_WOW64_64KEY
        )
        value, _ = regedit.QueryValueEx(handle, "MachineGuid")
        return value


def instance():
    '''
    Instance for facade proxy.
    '''
    return WinUniqueID()
