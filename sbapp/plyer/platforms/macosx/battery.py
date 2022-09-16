'''
Module of MacOS API for plyer.battery.
'''

from os import environ
from subprocess import Popen, PIPE
from plyer.facades import Battery
from plyer.utils import whereis_exe


class OSXBattery(Battery):
    '''
    Implementation of MacOS battery API.
    '''

    def _get_state(self):
        old_lang = environ.get('LANG', '')
        environ['LANG'] = 'C'

        status = {"isCharging": None, "percentage": None}

        ioreg_process = Popen(
            ["ioreg", "-rc", "AppleSmartBattery"],
            stdout=PIPE
        )
        output = ioreg_process.communicate()[0]

        environ['LANG'] = old_lang

        if not output:
            return status

        is_charging = max_capacity = current_capacity = None
        for line in output.decode('utf-8').splitlines():
            if 'IsCharging' in line:
                is_charging = line.rpartition('=')[-1].strip()
            if 'MaxCapacity' in line:
                max_capacity = float(line.rpartition('=')[-1].strip())
            if 'CurrentCapacity' in line:
                current_capacity = float(line.rpartition('=')[-1].strip())

        if is_charging:
            status['isCharging'] = is_charging == "Yes"

        if current_capacity and max_capacity:
            status['percentage'] = 100.0 * current_capacity / max_capacity

        return status


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('ioreg'):
        return OSXBattery()
    sys.stderr.write("ioreg not found.")
    return Battery()
