'''
Utils
=====

'''
__all__ = ('platform', 'reify', 'deprecated')

from os import environ
from os import path
from sys import platform as _sys_platform
import sys


class Platform:
    '''
    Refactored to class to allow module function to be replaced
    with module variable.
    '''

    def __init__(self):
        self._platform_ios = None
        self._platform_android = None

    def __eq__(self, other):
        return other == self._get_platform()

    def __ne__(self, other):
        return other != self._get_platform()

    def __str__(self):
        return self._get_platform()

    def __repr__(self):
        return 'platform name: \'{platform}\' from: \n{instance}'.format(
            platform=self._get_platform(),
            instance=super().__repr__()
        )

    def __hash__(self):
        return self._get_platform().__hash__()

    def _get_platform(self):

        if self._platform_android is None:
            # sys.getandroidapilevel is defined as of Python 3.7
            # ANDROID_ARGUMENT and ANDROID_PRIVATE are 2 environment variables
            # from python-for-android project
            self._platform_android = hasattr(sys, 'getandroidapilevel') or \
                'ANDROID_ARGUMENT' in environ

        if self._platform_ios is None:
            self._platform_ios = (environ.get('KIVY_BUILD', '') == 'ios')

        # On android, _sys_platform return 'linux2', so prefer to check the
        # import of Android module than trying to rely on _sys_platform.

        if self._platform_android is True:
            return 'android'
        elif self._platform_ios is True:
            return 'ios'
        elif _sys_platform in ('win32', 'cygwin'):
            return 'win'
        elif _sys_platform == 'darwin':
            return 'macosx'
        elif _sys_platform[:5] == 'linux':
            return 'linux'
        return 'unknown'


platform = Platform()


class Proxy:
    '''
    Based on http://code.activestate.com/recipes/496741-object-proxying
    version by Tomer Filiba, PSF license.
    '''

    __slots__ = ['_obj', '_name', '_facade']

    def __init__(self, name, facade):
        object.__init__(self)
        object.__setattr__(self, '_obj', None)
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_facade', facade)

    def _ensure_obj(self):
        obj = object.__getattribute__(self, '_obj')
        if obj:
            return obj
        # do the import
        try:
            name = object.__getattribute__(self, '_name')
            module = 'plyer.platforms.{}.{}'.format(
                platform, name)
            mod = __import__(module, fromlist='.')
            obj = mod.instance()
        except Exception:
            import traceback
            traceback.print_exc()
            facade = object.__getattribute__(self, '_facade')
            obj = facade()

        object.__setattr__(self, '_obj', obj)
        return obj

    def __getattribute__(self, name):
        result = None

        if name == '__doc__':
            return result

        # run _ensure_obj func, result in _obj
        object.__getattribute__(self, '_ensure_obj')()

        # return either Proxy instance or platform-dependent implementation
        result = getattr(object.__getattribute__(self, '_obj'), name)
        return result

    def __delattr__(self, name):
        object.__getattribute__(self, '_ensure_obj')()
        delattr(object.__getattribute__(self, '_obj'), name)

    def __setattr__(self, name, value):
        object.__getattribute__(self, '_ensure_obj')()
        setattr(object.__getattribute__(self, '_obj'), name, value)

    def __bool__(self):
        object.__getattribute__(self, '_ensure_obj')()
        return bool(object.__getattribute__(self, '_obj'))

    def __str__(self):
        object.__getattribute__(self, '_ensure_obj')()
        return str(object.__getattribute__(self, '_obj'))

    def __repr__(self):
        object.__getattribute__(self, '_ensure_obj')()
        return repr(object.__getattribute__(self, '_obj'))


def whereis_exe(program):
    ''' Tries to find the program on the system path.
        Returns the path if it is found or None if it's not found.
    '''
    path_split = ';' if platform == 'win' else ':'
    for pth in environ.get('PATH', '').split(path_split):
        folder = path.isdir(path.join(pth, program))
        available = path.exists(path.join(pth, program))
        if available and not folder:
            return path.join(pth, program)
    return None


class reify:
    '''
    Put the result of a method which uses this (non-data) descriptor decorator
    in the instance dict after the first call, effectively replacing the
    decorator with an instance variable.

    It acts like @property, except that the function is only ever called once;
    after that, the value is cached as a regular attribute. This gives you lazy
    attribute creation on objects that are meant to be immutable.

    Taken from the `Pyramid project <https://pypi.python.org/pypi/pyramid/>`_.

    To use this as a decorator::

         @reify
         def lazy(self):
              ...
              return hard_to_compute_int
         first_time = self.lazy   # lazy is reify obj, reify.__get__() runs
         second_time = self.lazy  # lazy is hard_to_compute_int
    '''

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, inst, cls):
        if inst is None:
            return self
        retval = self.func(inst)
        setattr(inst, self.func.__name__, retval)
        return retval


def deprecated(obj):
    '''
    This is a decorator which can be used to mark functions and classes as
    deprecated. It will result in a warning being emitted when a deprecated
    function is called or a new instance of a class created.

    In case of classes, the warning is emitted before the __new__ method
    of the decorated class is called, therefore a way before the __init__
    method itself.
    '''

    import warnings
    from inspect import stack
    from functools import wraps
    from types import FunctionType, MethodType

    new_obj = None

    # wrap a function into a function emitting a deprecated warning
    if isinstance(obj, FunctionType):

        @wraps(obj)
        def new_func(*args, **kwargs):
            # get the previous stack frame and extract file, line and caller
            # stack() -> caller()
            call_file, call_line, caller = stack()[1][1:4]

            # assemble warning
            warning = (
                'Call to deprecated function {} in {} line {}. '
                'Called from {} line {}'
                ' by {}().\n'.format(
                    obj.__name__,
                    obj.__code__.co_filename,
                    obj.__code__.co_firstlineno + 1,
                    call_file, call_line, caller
                )
            )

            warnings.warn('[{}] {}'.format('WARNING', warning))

            # if there is a docstring present, emit docstring too
            if obj.__doc__:
                warnings.warn(obj.__doc__)

            # return function wrapper
            return obj(*args, **kwargs)
        new_obj = new_func

    # wrap a class into a class emitting a deprecated warning
    # obj is class, type(obj) is metaclass, metaclasses inherit from type
    elif isinstance(type(obj), type):
        # we have an access to the metaclass instance (class) and need to print
        # the warning when a class instance (object) is created with __new__
        # i.e. when calling Class()

        def obj_new(cls, child, *args, **kwargs):
            '''
            Custom metaclass instance's __new__ method with deprecated warning.
            Calls the original __new__ method afterwards.
            '''
            # get the previous stack frame and extract file, line and caller
            # stack() -> caller()
            call_file, call_line, caller = stack()[1][1:4]
            loc_file = obj.__module__

            warnings.warn(
                '[{}] Creating an instance of a deprecated class {} in {}.'
                ' Called from {} line {} by {}().\n'.format(
                    'WARNING', obj.__name__, loc_file,
                    call_file, call_line, caller
                )
            )

            # if there is a docstring present, emit docstring too
            if obj.__doc__:
                warnings.warn(obj.__doc__)

            # make sure nothing silly gets into the function
            assert obj is cls

            # we are creating a __new__ for a class that inherits from
            # a deprecated class, therefore in this particular case
            # MRO is (child, cls, object) > (cls, object)
            if len(child.__mro__) > len(cls.__mro__):
                assert cls is child.__mro__[1], (cls.__mro__, child.__mro__)

            # we are creating __new__ directly for the deprecated class
            # therefore MRO is the same for parent and child class
            elif len(child.__mro__) == len(cls.__mro__):
                assert cls is child

            # return the class back with the extended __new__ method
            return obj.__old_new__(child)

        # back up the old __new__ method and create an extended
        # __new__ method that emits deprecated warnings
        obj.__old_new__ = obj.__new__
        obj.__new__ = MethodType(obj_new, obj)
        new_obj = obj

    # return a function wrapper or an extended class
    return new_obj
