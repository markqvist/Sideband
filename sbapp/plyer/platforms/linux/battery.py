'''
Module of Linux API for plyer.battery.
'''

from math import floor
from os import environ
from os.path import exists, join
from subprocess import Popen, PIPE
from plyer.facades import Battery
from plyer.utils import whereis_exe


class LinuxBattery(Battery):
    '''
    Implementation of Linux battery API via accessing the sysclass power_supply
    path from the kernel.
    '''

    def _get_state(self):
        status = {"isCharging": None, "percentage": None}

        kernel_bat_path = join('/sys', 'class', 'power_supply', 'BAT0')
        uevent = join(kernel_bat_path, 'uevent')

        with open(uevent) as fle:
            lines = [
                line.decode('utf-8').strip()
                for line in fle.readlines()
            ]
        output = {
            line.split('=')[0]: line.split('=')[1]
            for line in lines
        }

        is_charging = output['POWER_SUPPLY_STATUS'] == 'Charging'
        total = float(output['POWER_SUPPLY_CHARGE_FULL'])
        now = float(output['POWER_SUPPLY_CHARGE_NOW'])

        capacity = floor(now / total * 100)

        status['percentage'] = capacity
        status['isCharging'] = is_charging
        return status


class UPowerBattery(Battery):
    '''
    Implementation of UPower battery API.
    '''

    def _get_state(self):
        # if no LANG specified, return empty string
        old_lang = environ.get('LANG', '')
        environ['LANG'] = 'C'
        status = {"isCharging": None, "percentage": None}

        # We are supporting only one battery now
        # this will fail if there is no object with such path,
        # however it's safer than 'upower -d' which provides
        # multiple unrelated 'state' and 'percentage' keywords
        dev = "/org/freedesktop/UPower/devices/battery_BAT0"
        upower_process = Popen(
            ["upower", "--show-info", dev],
            stdout=PIPE
        )
        output = upower_process.communicate()[0].decode()
        environ['LANG'] = old_lang
        if not output:
            return status
        state = percentage = None

        for line in output.splitlines():
            if 'state' in line:
                state = line.rpartition(':')[-1].strip()

            if 'percentage' in line:
                percentage = line.rpartition(':')[-1].strip()[:-1]

                # switching decimal comma to dot
                # (different LC_NUMERIC locale)
                percentage = float(
                    percentage.replace(',', '.')
                )

        if state:
            status['isCharging'] = state == "charging"
        status['percentage'] = percentage
        return status


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('upower'):
        return UPowerBattery()
    sys.stderr.write("upower not found.")

    if exists(join('/sys', 'class', 'power_supply', 'BAT0')):
        return LinuxBattery()
    return Battery()
