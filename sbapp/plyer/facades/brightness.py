'''
Brightness
==========

This API helps you to control the brightness of your primary display screen.

The :class:`Brightness` provides access to public methods to control the
brightness of screen.

NOTE:: For Android, make sure to add permission, WRITE_SETTINGS

Simple Examples
---------------
To know the current brightness level of device::

    >>> from plyer import brightness
    >>> brightness.current_level()

To set the brightness level to half of maximum::

    >>> from plyer import brightness
    >>> brightness.set_level(50)

Supported Platforms
-------------------
Android, iOS, Linux
'''


class Brightness:
    '''
    Brightness facade.
    '''

    def current_level(self):
        '''
        Know the current level of device's brightness.
        '''
        return self._current_level()

    def set_level(self, level):
        '''
        Adjust the brightness of the screen.
        Minimum brightness level:: 1
        Maximum brightness level:: 100

        :param level: New level of brightness between 1 and 100
        :type level: int
        '''
        return self._set_level(level)

    # private

    def _set_level(self, level):
        raise NotImplementedError()

    def _current_level(self):
        raise NotImplementedError()
