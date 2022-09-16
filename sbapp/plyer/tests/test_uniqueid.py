'''
TestUniqueID
============

Tested platforms:

* Windows
'''

import unittest
from mock import patch, Mock
from plyer.tests.common import PlatformTest, platform_import


class TestUniqueID(unittest.TestCase):
    '''
    TestCase for plyer.uniqueid.
    '''

    def test_uniqueid(self):
        '''
        General all platform test for plyer.uniqueid.
        '''
        from plyer import uniqueid
        self.assertTrue(len(uniqueid.id) > 0)

    @PlatformTest('win')
    def test_uniqueid_win(self):
        '''
        Test Windows API for plyer.uniqueid.
        '''
        try:
            from winreg import (
                HKEY_LOCAL_MACHINE as HKLM,
                KEY_READ as READ, KEY_WOW64_64KEY as VIEW
            )
        except ImportError:
            from _winreg import (
                HKEY_LOCAL_MACHINE as HKLM,
                KEY_READ as READ, KEY_WOW64_64KEY as VIEW
            )

        # mock the 'regedit' alias for winreg,
        # see if the import passes and get the instance
        regedit_mod = 'plyer.platforms.win.uniqueid.regedit'
        with patch(target=regedit_mod):
            uniqueid_ = platform_import(
                platform='win',
                module_name='uniqueid'
            )
            uniqueid = uniqueid_.instance()
            self.assertIsInstance(uniqueid_.regedit, Mock)

        # out of mocking block, regedit should be a winreg module
        self.assertIsInstance(uniqueid_.regedit, type(unittest))

        # OpenKey is supposed to return a handle to registry key
        regedit_opkey = 'plyer.platforms.win.uniqueid.regedit.OpenKey'
        with patch(target=regedit_opkey, return_value='unicorn') as opkey:

            # QueryValueEx is supposed to return 2 packed values
            # (key, type_id)
            queryval = 'plyer.platforms.win.uniqueid.regedit.QueryValueEx'
            retval = ('unique', None)
            with patch(target=queryval, return_value=retval) as query:
                uid = uniqueid.id
                opkey.assert_called_once_with(
                    # key, subkey
                    HKLM, r'SOFTWARE\\Microsoft\\Cryptography',
                    # reserved integer (has to be 0 - zero), access mask
                    0, READ | VIEW
                )
                query.assert_called_once_with('unicorn', 'MachineGuid')
                self.assertEqual(uid, retval[0])


if __name__ == '__main__':
    unittest.main()
