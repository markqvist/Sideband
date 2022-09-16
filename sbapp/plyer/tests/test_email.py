'''
TestEmail
=========

Tested platforms:

* Windows
'''

import unittest

from mock import Mock, patch
from plyer.tests.common import PlatformTest, platform_import


class TestEmail(unittest.TestCase):
    '''
    TestCase for plyer.email.
    '''

    @staticmethod
    @PlatformTest('win')
    def test_email_win():
        '''
        Test starting Windows email client for plyer.email.
        '''
        email = platform_import(
            platform='win',
            module_name='email'
        )

        try:
            test_mailto = 'mailto:recipient?subject=subject&body=text'
            with patch(target='os.startfile', new=Mock()) as startfile:
                email.instance().send(
                    recipient='recipient',
                    subject='subject',
                    text='text'
                )
            startfile.assert_called_once_with(test_mailto)
        except WindowsError:
            # if WE is raised, email client isn't found,
            # but the platform code works correctly
            print('Mail client not found!')


if __name__ == '__main__':
    unittest.main()
