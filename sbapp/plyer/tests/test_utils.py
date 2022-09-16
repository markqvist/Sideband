'''
TestUtils
=========

Tested platforms:

* Android
* iOS
* Windows
* MacOS
* Linux
'''

import unittest
from mock import patch


class TestUtils(unittest.TestCase):
    '''
    TestCase for plyer.utils.
    '''

    def cutter(self, part, string):
        '''
        Cut off a part of a string if it contains a substring,
        otherwise raise an error.
        '''
        self.assertIn(part, string)
        return string[len(part):]

    def test_deprecated_function(self):
        '''
        Test printed out warning with @deprecated decorator
        on a function without any arguments.
        '''

        from plyer.utils import deprecated

        @deprecated
        def function():
            '''
            Dummy deprecated function.
            '''
            return 1

        with patch(target='warnings.warn') as stderr:
            self.assertEqual(function(), 1)

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function function', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_function().\n', args)

        args, _ = stderr.call_args_list[1]
        self.assertEqual(args, (
            '''
            Dummy deprecated function.
            ''',
        ))

    def test_deprecated_function_arg(self):
        '''
        Test printed out warning with @deprecated decorator
        on a function with arguments.
        '''

        from plyer.utils import deprecated

        @deprecated
        def function_with_arg(arg):
            '''
            Dummy deprecated function with arg.
            '''
            return arg

        with patch(target='warnings.warn') as stderr:
            self.assertEqual(function_with_arg(1), 1)

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function function_with_arg', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_function_arg().\n', args)

        args, _ = stderr.call_args_list[1]
        self.assertEqual(args, (
            '''
            Dummy deprecated function with arg.
            ''',
        ))

    def test_deprecated_function_kwarg(self):
        '''
        Test printed out warning with @deprecated decorator
        on a function with keyword arguments.
        '''

        from plyer.utils import deprecated

        @deprecated
        def function_with_kwarg(kwarg):
            '''
            Dummy deprecated function with kwarg.
            '''
            return kwarg

        with patch(target='warnings.warn') as stderr:
            self.assertEqual(function_with_kwarg(kwarg=1), 1)

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function function_with_kwarg', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_function_kwarg().\n', args)

        args, _ = stderr.call_args_list[1]
        self.assertEqual(args, (
            '''
            Dummy deprecated function with kwarg.
            ''',
        ))

    def test_deprecated_class_method(self):
        '''
        Test printed out warning with @deprecated decorator
        on a instance bound method.
        '''

        from plyer.utils import deprecated

        class Class:
            '''
            Dummy class with deprecated method method.
            '''
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            @deprecated
            def method(self):
                '''
                Dummy deprecated method.
                '''
                return (self.args, self.kwargs)

        with patch(target='warnings.warn') as stderr:
            args = (1, 2, 3)
            kwargs = dict(x=1, y=2)

            cls = Class(*args, **kwargs)
            self.assertEqual(cls.method(), (args, kwargs))

            args, kwargs = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function method', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_class_method().\n', args)

            args, kwargs = stderr.call_args_list[1]
            self.assertEqual(args, (
                '''
                Dummy deprecated method.
                ''',
            ))

    def test_deprecated_class_static_none(self):
        '''
        Test printed out warning with @deprecated decorator
        on a static method without arguments.
        '''

        from plyer.utils import deprecated

        class Class:
            '''
            Dummy class with deprecated static method.
            '''
            args = None
            kwargs = None

            def __init__(self, *args, **kwargs):
                Class.args = args
                Class.kwargs = kwargs

            @staticmethod
            @deprecated
            def static():
                '''
                Dummy deprecated static method.
                '''
                return (Class.args, Class.kwargs)

        with patch(target='warnings.warn') as stderr:
            self.assertEqual(Class.static(), (None, None))

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function static', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter(
                'by test_deprecated_class_static_none().\n', args
            )

            args, _ = stderr.call_args_list[1]
            self.assertEqual(args, (
                '''
                Dummy deprecated static method.
                ''',
            ))

    def test_deprecated_class_static_argskwargs(self):
        '''
        Test printed out warning with @deprecated decorator
        on a static method with arguments and keyword argument.
        '''

        from plyer.utils import deprecated

        class Class:
            '''
            Dummy class with deprecated static method.
            '''
            args = None
            kwargs = None

            def __init__(self, *args, **kwargs):
                Class.args = args
                Class.kwargs = kwargs

            @staticmethod
            @deprecated
            def static():
                '''
                Dummy deprecated static method.
                '''
                return (Class.args, Class.kwargs)

        with patch(target='warnings.warn') as stderr:
            args = (1, 2, 3)
            kwargs = dict(x=1, y=2)

            cls = Class(*args, **kwargs)
            self.assertEqual(cls.static(), (args, kwargs))

            args, kwargs = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function static', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter(
                'by test_deprecated_class_static_argskwargs().\n', args
            )

            args, kwargs = stderr.call_args_list[1]
            self.assertEqual(args, (
                '''
                Dummy deprecated static method.
                ''',
            ))

    def test_deprecated_class_clsmethod(self):
        '''
        Test printed out warning with @deprecated decorator
        on a class bound method.
        '''

        from plyer.utils import deprecated

        class Class:
            '''
            Dummy class with deprecated class method.
            '''
            args = None
            kwargs = None

            @classmethod
            @deprecated
            def clsmethod(cls):
                '''
                Dummy deprecated class method.
                '''
                return (cls.args, cls.kwargs)

        with patch(target='warnings.warn') as stderr:
            self.assertEqual(Class.clsmethod(), (None, None))

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('deprecated function clsmethod', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_class_clsmethod().\n', args)

            args, _ = stderr.call_args_list[1]
            self.assertEqual(args, (
                '''
                Dummy deprecated class method.
                ''',
            ))

    def test_deprecated_class(self):
        '''
        Test printed out warning with @deprecated decorator on a class.
        '''

        from plyer.utils import deprecated

        @deprecated
        class Class:
            '''
            Dummy deprecated class.
            '''
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        with patch(target='warnings.warn') as stderr:
            args = (1, 2, 3)
            kwargs = dict(x=1, y=2)

            cls = Class(*args, **kwargs)
            self.assertIsInstance(cls, Class)
            self.assertEqual(cls.args, args)
            self.assertEqual(cls.kwargs, kwargs)

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('Creating an instance', args)
            args = self.cutter('deprecated class Class in', args)
            args = self.cutter(__name__, args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_class().\n', args)

        args, kwargs = stderr.call_args_list[1]
        self.assertEqual(args, (
            '''
            Dummy deprecated class.
            ''',
        ))

    def test_deprecated_class_inherited(self):
        '''
        Test printed out warning with @deprecated decorator on a class
        which inherits from a deprecated class.
        '''

        from plyer.utils import deprecated

        @deprecated
        class Class:
            '''
            Dummy deprecated class.
            '''
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        class Inherited(Class):
            '''
            Dummy class inheriting from a dummy deprecated class.
            '''
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.args = args
                self.kwargs = kwargs

        with patch(target='warnings.warn') as stderr:
            args = (1, 2, 3)
            kwargs = dict(x=1, y=2)

            cls = Inherited(*args, **kwargs)
            self.assertIsInstance(cls, Inherited)
            self.assertEqual(cls.args, args)
            self.assertEqual(cls.kwargs, kwargs)

            args, _ = stderr.call_args_list[0]
            args = args[0]
            args = self.cutter('[WARNING] ', args)
            args = self.cutter('Creating an instance', args)
            args = self.cutter('deprecated class Class in', args)
            args = self.cutter(__name__, args)
            args = self.cutter('Called from', args)
            args = self.cutter('test_utils.py', args)
            args = self.cutter('by test_deprecated_class_inherited().\n', args)

        args, kwargs = stderr.call_args_list[1]
        self.assertEqual(args, (
            '''
            Dummy deprecated class.
            ''',
        ))


if __name__ == '__main__':
    unittest.main()
