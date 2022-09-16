'''
TestBluetooth
=============

Tested platforms:

* macOS - system_profiler
'''

import unittest

from plyer.tests.common import platform_import
from textwrap import dedent


class MockedSystemProfiler:
    '''
    Mocked object used instead of Apple's system_profiler
    '''
    value = "On"
    output = dedent(
        """Bluetooth:

      Apple Bluetooth Software Version: 6.0.7f11
      Hardware, Features, and Settings:
          Address: AA-00-BB-11-CC-22
          Bluetooth Low Energy Supported: Yes
          Handoff Supported: Yes
          Instant Hot Spot Supported: Yes
          Manufacturer: Broadcom
          Transport: UART
          Chipset: 1234
          Firmware Version: v00 c0000
          Bluetooth Power: {}
          Auto Seek Pointing: On
          Remote wake: On
          Vendor ID: 0x0000
          Product ID: 0x0000
          HCI Version:  (0x0)
          HCI Revision: 0x0000
          LMP Version:  (0x0)
          LMP Subversion: 0x0000
          Auto Seek Keyboard: On
      Devices (Paired, Configured, etc.):
          iPhone:
              Address: AA-00-BB-11-CC-22
              Major Type: Miscellaneous
              Minor Type: Unknown
              Services:
              Paired: No
              Configured: Yes
              Connected: No
              Class of Device: 0x00 0x00 0x0000
      Services:
          Bluetooth File Transfer:
              Folder other devices can browse: ~/Public
              When receiving items: Accept all without warning
              State: Disabled
          Bluetooth File Exchange:
              Folder for accepted items: ~/Downloads
              When other items are accepted: Save to location
              When receiving items: Accept all without warning
              State: Disabled
          Bluetooth Internet Sharing:
              State: Disabled
      Incoming Serial Ports:
          Bluetooth-Incoming-Port:
              RFCOMM Channel: 3
              Requires Authentication: No"""
    ).format(value).encode('utf-8')

    def __init__(self, *args, **kwargs):
        # only to ignore all args, kwargs
        pass

    @staticmethod
    def communicate():
        '''
        Mock Popen.communicate, so that 'system_profiler'
        isn't used.
        '''
        return (MockedSystemProfiler.output, )

    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        macOS system_profiler binary is present on the system.
        '''
        return binary == 'system_profiler'

    @staticmethod
    def get_info():
        '''
        Return current bluetooth status from mocked output.
        '''
        return MockedSystemProfiler.value


class TestBluetooth(unittest.TestCase):
    '''
    TestCase for plyer.bluetooth.
    '''

    def test_bluetooth_macosx(self):
        '''
        Test macOS system_profiler for plyer.bluetooth.
        '''
        bluetooth = platform_import(
            platform='macosx',
            module_name='bluetooth',
            whereis_exe=MockedSystemProfiler.whereis_exe
        )

        bluetooth.Popen = MockedSystemProfiler
        self.assertIn('OSXBluetooth', dir(bluetooth))
        bluetooth = bluetooth.instance()
        self.assertIn('OSXBluetooth', str(bluetooth))

        self.assertEqual(
            bluetooth.info, MockedSystemProfiler.get_info()
        )

    def test_bluetooth_macosx_instance(self):
        '''
        Test macOS instance for plyer.bluetooth.
        '''

        def no_exe(*args, **kwargs):
            return

        bluetooth = platform_import(
            platform='macosx',
            module_name='bluetooth',
            whereis_exe=no_exe
        )

        bluetooth = bluetooth.instance()
        self.assertNotIn('OSXBluetooth', str(bluetooth))
        self.assertIn('Bluetooth', str(bluetooth))


if __name__ == '__main__':
    unittest.main()
