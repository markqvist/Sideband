'''
TestStoragePath
===============

Tested platforms:

* macOS
'''

import unittest

from plyer.tests.common import platform_import, PlatformTest


class TestStoragePath(unittest.TestCase):
    '''
    TestCase for plyer.storagepath.
    '''

    @PlatformTest('macosx')
    def test_storagepath_macosx(self):
        '''
        Test macOS for plyer.storagepath.
        '''
        storagepath = platform_import(
            platform='macosx',
            module_name='storagepath'
        )

        self.assertIn('OSXStoragePath', dir(storagepath))
        storagepath = storagepath.instance()
        self.assertIn('OSXStoragePath', str(storagepath))

        path_format = 'file:///Users/'

        self.assertIn(path_format, storagepath.get_home_dir())
        self.assertIn('/', storagepath.get_root_dir())
        self.assertIn(path_format, storagepath.get_documents_dir())
        self.assertIn(path_format, storagepath.get_downloads_dir())
        self.assertIn(path_format, storagepath.get_videos_dir())
        self.assertIn(path_format, storagepath.get_music_dir())
        self.assertIn(path_format, storagepath.get_pictures_dir())
        self.assertIn(path_format, storagepath.get_application_dir())

    @PlatformTest('win')
    def test_storagepath_windows(self):
        '''
        Test win for plyer.storagepath.
        '''
        storagepath = platform_import(
            platform='win',
            module_name='storagepath'
        )

        self.assertIn('WinStoragePath', dir(storagepath))
        storagepath = storagepath.instance()
        self.assertIn('WinStoragePath', str(storagepath))

        path_format = ':\\'

        self.assertIn(path_format, storagepath.get_home_dir())
        self.assertIn(path_format, storagepath.get_root_dir())
        self.assertIn(path_format, storagepath.get_documents_dir())
        self.assertIn(path_format, storagepath.get_downloads_dir())
        self.assertIn(path_format, storagepath.get_videos_dir())
        self.assertIn(path_format, storagepath.get_music_dir())
        self.assertIn(path_format, storagepath.get_pictures_dir())
        self.assertIn(path_format, storagepath.get_application_dir())


if __name__ == '__main__':
    unittest.main()
