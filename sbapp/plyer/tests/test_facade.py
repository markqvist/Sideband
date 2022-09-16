'''
TestFacade
==========

Tested platforms:

* Android
* iOS
* Windows
* MacOS
* Linux
'''

import unittest

import sys
from types import MethodType

from mock import Mock, patch

import plyer


def mock_platform_module(mod, platform, cls):
    '''
    Create a stub module for a specific platform. This module contains:

    * class inheriting from facade implementing the desired feature
    * 'instance' function returning an instance of the implementing class
    '''

    # assemble an instance returned from the instance() function
    # which is created from a dynamically created class
    # <class '<mod>.<platform><cls>'> e.g.:
    # <class 'plyer.platforms.win.dummy . WinDummy'>
    stub_inst = Mock(
        __module__=mod,
        __class__=type(
            '{}{}'.format(platform.title(), cls), (object, ), {
                '__module__': mod
            }
        ),
    )

    # manual 'return_value' assign to Mock, so that the instance() call
    # can return stub_inst's own instance instead of creating another
    # unnecessary Mock object
    stub_inst.return_value = stub_inst

    # bind custom function returning the class name to stub_inst instance,
    # so that instance().show() call requires 'self' i.e. instance parameter
    # for the function to access the instance's class name
    stub_inst.show = MethodType(lambda slf: slf, stub_inst)

    stub_mod = Mock(instance=stub_inst)
    return stub_mod


# dummy pyjnius class to silence the import + config
class DummyJnius:
    '''
    Mocked PyJNIus module.
    '''

    def __init__(self, *args, **kwargs):
        class JavaClass:
            '''
            Mocked PyJNIus JavaClass object.
            '''

            def __init__(self):
                self.ANDROID_VERSION = None
                self.SDK_INT = 1
                self.mActivity = None

        self.autoclass = lambda *a, **kw: JavaClass()


class TestFacade(unittest.TestCase):
    '''
    TestCase for plyer.utils.Proxy and plyer.facades.
    '''

    def test_facade_existing_platforms(self):
        '''
        Test for returning an object for Android API implementation
        from Proxy object using a dynamically generated dummy objects.
        '''
        _original = plyer.utils.platform

        for plat in {'android', 'ios', 'win', 'macosx', 'linux'}:
            plyer.utils.platform = plat

            if plat == 'android':
                # android platform automatically imports jnius
                sys.modules['jnius'] = DummyJnius()

            # create stub module with instance func and class
            stub_mod = mock_platform_module(
                mod='plyer.platforms.{}.dummy'.format(plat),
                platform=plyer.utils.platform,
                cls='Dummy'
            )

            proxy_cls = plyer.utils.Proxy
            target = 'builtins.__import__'

            with patch(target=target, return_value=stub_mod):
                dummy = proxy_cls('dummy', stub_mod)

                self.assertEqual(
                    str(dummy.__class__).split("'")[1],
                    'plyer.platforms.{}.dummy.{}Dummy'.format(
                        plat, plat.title()
                    )
                )
                self.assertEqual(
                    str(dummy.show().__class__).split("'")[1],
                    'plyer.platforms.{}.dummy.{}Dummy'.format(
                        plat, plat.title()
                    )
                )

        plyer.utils.platform = _original

    def test_facade_unknown(self):
        '''
        Test fallback of Proxy to facade if there
        is no such requested platform.
        '''

        _original = plyer.utils.platform
        plyer.utils.platform = 'unknown'

        # no 'unknown' platform (folder), fallback to facade
        class MockedProxy(plyer.utils.Proxy):
            '''
            Partially mocked Proxy class, so that we pull the error
            from traceback.print_exc to the test and check the calls.
            '''

            # _ensure_obj is called only once, to either
            # get the platform object or fall back to facade
            # therefore the three self.asserts below will return
            # different values
            expected_asserts = [True, False, False]

            def _ensure_obj(inst):
                # called once, prints to stderr

                # mock stderr because traceback.print_exc uses it
                # https://github.com/python/cpython/blob/
                # 16dfca4d829e45f36e71bf43f83226659ce49315/Lib/traceback.py#L99
                sys.stderr = Mock()

                # call the original function to trigger
                # ImportError warnings in stderr
                super(MockedProxy, inst)._ensure_obj()

                # Traceback (most recent call last):
                #   File "/app/plyer/utils.py", line 88, in _ensure_obj
                #     mod = __import__(module, fromlist='.')
                # ImportError: No module named unknown.dummy

                # must not use self.assertX
                # (has to be checked on the go!)
                expected_bool = MockedProxy.expected_asserts.pop(0)
                call_count = sys.stderr.write.call_count
                assert (call_count == 6) == expected_bool, call_count

                # return stderr to the original state
                sys.stderr = sys.__stderr__

        proxy_cls = MockedProxy
        facade = Mock()
        dummy = proxy_cls('dummy', facade)

        self.assertEqual(dummy._mock_new_parent, facade)
        plyer.utils.platform = _original


if __name__ == '__main__':
    unittest.main()
