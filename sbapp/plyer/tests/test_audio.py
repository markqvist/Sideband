'''
TestAudio
=========

Tested platforms:

* macOS
* Windows

.. versionadded:: 1.4.0
'''

import unittest
import time

from os import mkdir, remove, environ
from os.path import join, expanduser, exists
from plyer.tests.common import platform_import, PlatformTest


class TestAudio(unittest.TestCase):
    '''
    TestCase for plyer.audio.

    .. versionadded:: 1.4.0
    '''

    @PlatformTest('macosx')
    def test_audio_macosx(self):
        '''
        Test macOS audio start, stop and play

        .. versionadded:: 1.4.0
        '''

        path = join(expanduser('~'), 'Music')
        if not exists(path):
            mkdir(path)

        audio = platform_import(
            platform='macosx',
            module_name='audio',
        )

        self.assertIn('OSXAudio', dir(audio))
        audio = audio.instance()
        self.assertIn('OSXAudio', str(audio))

        self.assertFalse(exists(audio.file_path))
        self.assertIsNone(audio.start())
        time.sleep(0.5)
        self.assertIsNone(audio.stop())
        self.assertIsNone(audio.play())
        time.sleep(0.5)
        self.assertIsNone(audio.stop())

        audio.file_path = audio.file_path.replace(
            'file://', ''
        )

        self.assertTrue(exists(audio.file_path))

        remove(audio.file_path)

    @PlatformTest('win')
    def test_audio_win(self):
        '''
        Test Windows audio start, stop and play

        .. versionadded:: 1.4.0
        '''

        if environ.get('APPVEYOR'):
            # Appveyor has no recording device installed
            # therefore the test will 100% fail
            #
            # error_code: 328
            # message:
            # 'No wave device is installed that can record files in the current
            # format. To install a wave device, go to Control Panel, click P')
            return

        path = join(environ['USERPROFILE'], 'Music')
        if not exists(path):
            mkdir(path)

        audio = platform_import(
            platform='win',
            module_name='audio',
        )

        self.assertIn('WinAudio', dir(audio))
        audio = audio.instance()
        self.assertIn('WinAudio', str(audio))

        self.assertFalse(exists(audio.file_path))
        self.assertIsNone(audio.start())
        time.sleep(0.5)
        self.assertIsNone(audio.stop())
        self.assertIsNone(audio.play())
        time.sleep(0.5)
        self.assertIsNone(audio.stop())

        self.assertTrue(exists(audio.file_path))

        remove(audio.file_path)


if __name__ == '__main__':
    unittest.main()
