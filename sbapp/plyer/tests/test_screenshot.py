'''
TestScreenshot
==============

Tested platforms:

* MacOS
* Linux
'''

import unittest

from os import mkdir, remove
from os.path import join, expanduser, exists

from mock import patch
from plyer.tests.common import PlatformTest, platform_import


class MockedScreenCapture:
    '''
    Mocked object used instead of the console-like calling
    of screencapture binary with parameters.
    '''
    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        MacOS screencapture binary is present on the system.
        '''
        return binary == 'screencapture'

    @staticmethod
    def call(args):
        '''
        Mocked subprocess.call to check console parameters.
        '''
        assert len(args) == 2, len(args)
        assert args[0] == 'screencapture', args
        assert args[1] == join(
            expanduser('~'), 'Pictures', 'screenshot.png'
        ), args
        with open(args[1], 'w') as scr:
            scr.write('')


class MockedXWD:
    '''
    Mocked object used instead of the console-like calling
    of X11 xwd binary with parameters.
    '''
    @staticmethod
    def whereis_exe(binary):
        '''
        Mock whereis_exe, so that it looks like
        X11 xwd binary is present on the system.
        '''
        return binary == 'xwd'

    @staticmethod
    def call(args, stdout):
        '''
        Mocked subprocess.call to check console parameters.
        '''
        assert len(args) == 3, args
        assert args[0] == 'xwd', args
        assert args[1:] == ['-silent', '-root'], args
        assert stdout.name == join(
            expanduser('~'), 'Pictures', 'screenshot.xwd'
        ), stdout.name
        with open(stdout.name, 'w') as scr:
            scr.write('')


class TestScreenshot(unittest.TestCase):
    '''
    TestCase for plyer.screenshot.
    '''

    def setUp(self):
        path = join(expanduser('~'), 'Pictures')
        if not exists(path):
            mkdir(path)

    @PlatformTest('macosx')
    def test_screenshot_screencapture(self):
        '''
        Test mocked MacOS screencapture for plyer.screenshot.
        '''
        scr = platform_import(
            platform='macosx',
            module_name='screenshot',
            whereis_exe=MockedScreenCapture.whereis_exe
        )

        # such class exists in screenshot module
        self.assertIn('OSXScreenshot', dir(scr))

        # the required instance is created
        scr = scr.instance()
        self.assertIn('OSXScreenshot', str(scr))

        # move capture from context manager to run without mock
        with patch(target='subprocess.call', new=MockedScreenCapture.call):
            self.assertIsNone(scr.capture())

        self.assertTrue(exists(scr.file_path))
        remove(scr.file_path)

    @PlatformTest('linux')
    def test_screenshot_xwd(self):
        '''
        Test mocked X11 xwd for plyer.screenshot.
        '''
        scr = platform_import(
            platform='linux',
            module_name='screenshot',
            whereis_exe=MockedXWD.whereis_exe
        )

        # such class exists in screenshot module
        self.assertIn('LinuxScreenshot', dir(scr))

        # the required instance is created
        scr = scr.instance()
        self.assertIn('LinuxScreenshot', str(scr))

        # move capture from context manager to run without mock
        with patch(target='subprocess.call', new=MockedXWD.call):
            self.assertIsNone(scr.capture())

        self.assertTrue(exists(scr.file_path))
        remove(scr.file_path)


if __name__ == '__main__':
    unittest.main()
