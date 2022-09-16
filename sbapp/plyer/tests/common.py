'''
Common objects for testing
==========================

* :class:`PlatformTest` - used as a decorator, allows running a test function
  only on a specific platform (see `plyer.utils.platform`).
* :func:`platform_import` - manual import of a platform specific class instead
  of using `plyer.facades.*` proxies.
'''

import traceback
from os import sep
from os.path import normpath, splitdrive
from plyer.utils import platform as plyer_platform


class PlatformTest:
    '''
    Class for the @PlatformTest decorator to prevent running tests
    calling platform dependent API on different platforms.
    '''

    def __init__(self, platform):
        self.platform = platform

    def __call__(self, func):
        platform = self.platform

        if platform != plyer_platform:
            print("Skipping test '{}' - not on '{}'".format(
                func.__name__, platform
            ))
            func = self.eat
        return func

    @staticmethod
    def eat(*args, **kwargs):
        '''
        Simply eat all positional and keyword arguments
        and return None as an empty function.
        '''


def platform_import(platform, module_name, whereis_exe=None):
    '''
    Import platform API directly instead of through Proxy.
    '''

    try:
        module = 'plyer.platforms.{}.{}'.format(
            platform, module_name
        )
        mod = __import__(module, fromlist='.')

    except ImportError as exc:
        print(vars(exc))
        traceback.print_exc()

    if whereis_exe:
        mod.whereis_exe = whereis_exe
    return mod


def splitpath(path):
    '''
    Split string path into a list of folders (+ file if available).
    '''
    if path[0] == sep and path[1] != sep:
        path = path[1:]
        path = normpath(path).split(sep)
    else:
        drive, path = splitdrive(path)
        if path[0] == sep and path[1] != sep:
            path = path[1:]
        path = [drive, ] + normpath(path).split(sep)
    return path
