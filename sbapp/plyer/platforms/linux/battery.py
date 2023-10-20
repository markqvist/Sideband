'''
Module of Linux API for plyer.battery.
'''

import os
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

        kernel_bat_path = join('/sys', 'class', 'power_supply', self.node_name)
        uevent = join(kernel_bat_path, 'uevent')

        with open(uevent, "rb") as fle:
            lines = [
                line.decode('utf-8').strip()
                for line in fle.readlines()
            ]
        output = {
            line.split('=')[0]: line.split('=')[1]
            for line in lines
        }

        is_charging = output['POWER_SUPPLY_STATUS'] == 'Charging'
        charge_percent = float(output['POWER_SUPPLY_CAPACITY'])

        status['percentage'] = charge_percent
        status['isCharging'] = is_charging
        return status


def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    # if whereis_exe('upower'):
    #     return UPowerBattery()
    # sys.stderr.write("upower not found.")

    node_exists = False
    bn = 0
    node_name = None
    for bi in range(0,10):
        path = join('/sys', 'class', 'power_supply', 'BAT'+str(bi))
        if os.path.isdir(path):
            node_name = "BAT"+str(bi)
            break

    if node_name:
        b = LinuxBattery()
        b.node_name = node_name
        return b

    return Battery()
