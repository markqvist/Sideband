'''
TestBattery
===========

Tested platforms:

* Windows
* Linux - upower, kernel sysclass
* macOS - ioreg
'''

import unittest
from io import BytesIO
from os.path import join
from textwrap import dedent
from mock import patch, Mock

from plyer.tests.common import PlatformTest, platform_import


class MockedKernelSysclass:
    '''
    Mocked object used instead of Linux's sysclass for power_supply
    battery uevent.
    '''

    @property
    def path(self):
        '''
        Mocked path to Linux kernel sysclass.
        '''
        return join('/sys', 'class', 'power_supply', 'BAT0')

    @property
    def charging(self):
        '''
        Mocked battery charging status.
        '''
        return u'Discharging'

    @property
    def percentage(self):
        '''
        Mocked battery charge percentage.
        '''
        return 89.0

    @property
    def full(self):
        '''
        Mocked full battery charge.
        '''
        return 4764000

    @property
    def now(self):
        '''
        Calculated current mocked battery charge.
        '''
        return self.percentage * self.full / 100.0

    @property
    def uevent(self):
        '''
        Mocked /sys/class/power_supply/BAT0 file.
        '''
        return BytesIO(dedent(b'''\
            POWER_SUPPLY_NAME=BAT0
            POWER_SUPPLY_STATUS={}
            POWER_SUPPLY_PRESENT=1
            POWER_SUPPLY_TECHNOLOGY=Li-ion
            POWER_SUPPLY_CYCLE_COUNT=0
            POWER_SUPPLY_VOLTAGE_MIN_DESIGN=10800000
            POWER_SUPPLY_VOLTAGE_NOW=12074000
            POWER_SUPPLY_CURRENT_NOW=1584000
            POWER_SUPPLY_CHARGE_FULL_DESIGN=5800000
            POWER_SUPPLY_CHARGE_FULL={}
            POWER_SUPPLY_CHARGE_NOW={}
            POWER_SUPPLY_CAPACITY={}
            POWER_SUPPLY_CAPACITY_LEVEL=Normal
            POWER_SUPPLY_MODEL_NAME=1005HA
            POWER_SUPPLY_MANUFACTURER=ASUS
            POWER_SUPPLY_SERIAL_NUMBER=0
        '''.decode('utf-8').format(
            self.charging, self.full,
            self.now, int(self.percentage)
        )).encode('utf-8'))


class MockedUPower:
    '''
    Mocked object used instead of 'upower' binary in the Linux specific API
    plyer.platforms.linux.battery. The same output structure is tested for
    the range of <min_version, max_version>.

    .. note:: Extend the object with another data sample if it does not match.
    '''

    min_version = '0.99.4'
    max_version = '0.99.4'

    values = {
        u'Device': u'/org/freedesktop/UPower/devices/battery_BAT0',
        u'native-path': u'BAT0',
        u'vendor': u'ASUS',
        u'model': u'1005HA',
        u'power supply': u'yes',
        u'updated': u'Thu 05 Jul 2018 23:15:01 PM CEST',
        u'has history': u'yes',
        u'has statistics': u'yes',
        u'battery': {
            u'present': u'yes',
            u'rechargeable': u'yes',
            u'state': u'discharging',
            u'warning-level': u'none',
            u'energy': u'48,708 Wh',
            u'energy-empty': u'0 Wh',
            u'energy-full': u'54,216 Wh',
            u'energy-full-design': u'62,64 Wh',
            u'energy-rate': u'7,722 W',
            u'voltage': u'11,916 V',
            u'time to empty': u'6,3 hours',
            u'percentage': u'89%',
            u'capacity': u'86,5517%',
            u'technology': u'lithium-ion',
            u'icon-name': u"'battery-full-symbolic"
        },
        u'History (charge)': u'1530959637  89,000  discharging',
        u'History (rate)': u'1530958556  7,474   discharging'
    }

    data = str(
        '  native-path:          {native-path}\n'
        '  vendor:               {vendor}\n'
        '  model:                {model}\n'
        '  power supply:         {power supply}\n'
        '  updated:              {updated}\n'
        '  has history:          {has history}\n'
        '  has statistics:       {has statistics}\n'
        '  battery\n'
        '    present:              {battery[present]}\n'
        '    rechargeable:         {battery[rechargeable]}\n'
        '    state:                {battery[state]}\n'
        '    warning-level:        {battery[warning-level]}\n'
        '    energy:               {battery[energy]}\n'
        '    energy-empty:         {battery[energy-empty]}\n'
        '    energy-full:          {battery[energy-full]}\n'
        '    energy-full-design:   {battery[energy-full-design]}\n'
        '    energy-rate:          {battery[energy-rate]}\n'
        '    voltage:              {battery[voltage]}\n'
        '    time to empty:        {battery[time to empty]}\n'
        '    percentage:           {battery[percentage]}\n'
        '    capacity:             {battery[capacity]}\n'
        '    technology:           {battery[technology]}\n'
        '    icon-name:            {battery[icon-name]}\n'
        '  History (charge):\n'
        '    {History (charge)}\n'
        '  History (rate):\n'
        '    {History (rate)}\n'
    ).format(**values).encode('utf-8')
    # LinuxBattery calls decode()

    def __init__(self, *args, **kwargs):
        # only to ignore all args, kwargs
        pass

    @staticmethod
    def communicate():
        '''
        Mock Popen.communicate, so that 'upower' isn't used.
        '''
        return (MockedUPower.data, )

    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        Linux UPower binary is present on the system.
        '''
        return binary == 'upower'

    @staticmethod
    def charging():
        '''
        Return charging bool from mocked data.
        '''
        return MockedUPower.values['battery']['state'] == 'charging'

    @staticmethod
    def percentage():
        '''
        Return percentage from mocked data.
        '''
        percentage = MockedUPower.values['battery']['percentage'][:-1]
        return float(percentage.replace(',', '.'))


class MockedIOReg:
    '''
    Mocked object used instead of Apple's ioreg.
    '''
    values = {
        "MaxCapacity": "5023",
        "CurrentCapacity": "4222",
        "IsCharging": "No"
    }

    output = dedent(
        """+-o AppleSmartBattery  <class AppleSmartBattery,\
    id 0x1000002c9, registered, matched, active, busy 0 (0 ms), retain 6>
    {{
      "TimeRemaining" = 585
      "AvgTimeToEmpty" = 585
      "InstantTimeToEmpty" = 761
      "ExternalChargeCapable" = Yes
      "FullPathUpdated" = 1541845134
      "CellVoltage" = (4109,4118,4099,0)
      "PermanentFailureStatus" = 0
      "BatteryInvalidWakeSeconds" = 30
      "AdapterInfo" = 0
      "MaxCapacity" = {MaxCapacity}
      "Voltage" = 12326
      "DesignCycleCount70" = 13
      "Manufacturer" = "SWD"
      "Location" = 0
      "CurrentCapacity" = {CurrentCapacity}
      "LegacyBatteryInfo" = {{"Amperage"=18446744073709551183,"Flags"=4,\
      "Capacity"=5023,"Current"=4222,"Voltage"=12326,"Cycle Count"=40}}
      "FirmwareSerialNumber" = 1
      "BatteryInstalled" = Yes
      "PackReserve" = 117
      "CycleCount" = 40
      "DesignCapacity" = 5088
      "OperationStatus" = 58435
      "ManufactureDate" = 19700
      "AvgTimeToFull" = 65535
      "BatterySerialNumber" = "1234567890ABCDEFGH"
      "BootPathUpdated" = 1541839734
      "PostDischargeWaitSeconds" = 120
      "Temperature" = 3038
      "UserVisiblePathUpdated" = 1541845194
      "InstantAmperage" = 18446744073709551249
      "ManufacturerData" = <000000000>
      "FullyCharged" = No
      "MaxErr" = 1
      "DeviceName" = "bq20z451"
      "IOGeneralInterest" = "IOCommand is not serializable"
      "Amperage" = 18446744073709551183
      "IsCharging" = {IsCharging}
      "DesignCycleCount9C" = 1000
      "PostChargeWaitSeconds" = 120
      "ExternalConnected" = No
    }}"""
    ).format(**values).encode('utf-8')

    def __init__(self, *args, **kwargs):
        # only to ignore all args, kwargs
        pass

    @staticmethod
    def communicate():
        '''
        Mock Popen.communicate, so that 'ioreg' isn't used.
        '''
        return (MockedIOReg.output, )

    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        macOS ioreg binary is present on the system.
        '''
        return binary == 'ioreg'

    @staticmethod
    def charging():
        '''
        Return charging bool from mocked data.
        '''
        return MockedIOReg.values['IsCharging'] == 'Yes'

    @staticmethod
    def percentage():
        '''
        Return percentage from mocked data.
        '''
        current_capacity = int(MockedIOReg.values['CurrentCapacity'])
        max_capacity = int(MockedIOReg.values['MaxCapacity'])
        percentage = 100.0 * current_capacity / max_capacity

        return percentage


class TestBattery(unittest.TestCase):
    '''
    TestCase for plyer.battery.
    '''

    def test_battery_linux_upower(self):
        '''
        Test mocked Linux UPower for plyer.battery.
        '''
        battery = platform_import(
            platform='linux',
            module_name='battery',
            whereis_exe=MockedUPower.whereis_exe
        )
        battery.Popen = MockedUPower
        battery = battery.instance()

        self.assertEqual(
            battery.status, {
                'isCharging': MockedUPower.charging(),
                'percentage': MockedUPower.percentage()
            }
        )

    def test_battery_linux_kernel(self):
        '''
        Test mocked Linux kernel sysclass for plyer.battery.
        '''

        def false(*args, **kwargs):
            return False

        sysclass = MockedKernelSysclass()

        with patch(target='os.path.exists') as bat_path:
            # first call to trigger exists() call
            platform_import(
                platform='linux',
                module_name='battery',
                whereis_exe=false
            ).instance()
            bat_path.assert_called_once_with(sysclass.path)

            # exists() checked with sysclass path
            # set mock to proceed with this branch
            bat_path.return_value = True

            battery = platform_import(
                platform='linux',
                module_name='battery',
                whereis_exe=false
            ).instance()

        stub = Mock(return_value=sysclass.uevent)
        target = 'builtins.open'

        with patch(target=target, new=stub):
            self.assertEqual(
                battery.status, {
                    'isCharging': sysclass.charging == 'Charging',
                    'percentage': sysclass.percentage
                }
            )

    @PlatformTest('win')
    def test_battery_win(self):
        '''
        Test Windows API for plyer.battery.
        '''
        battery = platform_import(
            platform='win',
            module_name='battery'
        ).instance()
        for key in ('isCharging', 'percentage'):
            self.assertIn(key, battery.status)
            self.assertIsNotNone(battery.status[key])

    def test_battery_macosx(self):
        '''
        Test macOS IOReg for plyer.battery.
        '''
        battery = platform_import(
            platform='macosx',
            module_name='battery',
            whereis_exe=MockedIOReg.whereis_exe
        )

        battery.Popen = MockedIOReg
        self.assertIn('OSXBattery', dir(battery))
        battery = battery.instance()
        self.assertIn('OSXBattery', str(battery))

        self.assertEqual(
            battery.status, {
                'isCharging': MockedIOReg.charging(),
                'percentage': MockedIOReg.percentage()
            }
        )

    def test_battery_macosx_instance(self):
        '''
        Test macOS instance for plyer.battery
        '''

        def no_exe(*args, **kwargs):
            return

        battery = platform_import(
            platform='macosx',
            module_name='battery',
            whereis_exe=no_exe
        )

        battery = battery.instance()
        self.assertNotIn('OSXBattery', str(battery))
        self.assertIn('Battery', str(battery))


if __name__ == '__main__':
    unittest.main()
