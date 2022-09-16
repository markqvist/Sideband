'''
Module of MacOS API for plyer.bluetooth.
'''

from subprocess import Popen, PIPE
from plyer.facades import Bluetooth
from plyer.utils import whereis_exe

from os import environ


class OSXBluetooth(Bluetooth):
    '''
    Implementation of MacOS bluetooth API.
    '''

    def _get_info(self):
        old_lang = environ.get('LANG')
        environ['LANG'] = 'C'

        sys_profiler_process = Popen(
            ["system_profiler", "SPBluetoothDataType"],
            stdout=PIPE
        )

        stdout = sys_profiler_process.communicate()[0].decode('utf-8')
        output = stdout.splitlines()

        lines = []
        for line in output:
            if 'Bluetooth Power' not in line:
                continue
            lines.append(line)

        if old_lang is None:
            environ.pop('LANG')
        else:
            environ['LANG'] = old_lang

        if output and len(lines) == 1:
            return lines[0].split()[2]
        else:
            return None


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('system_profiler'):
        return OSXBluetooth()
    sys.stderr.write("system_profiler not found.")
    return Bluetooth()
