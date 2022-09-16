'''
Accelerometer
============

The accelerometer is a motion sensor that detects the change (delta) in
movement relative to the current device orientation, in three dimensions
along the x, y, and z axis.

The :class:`Accelerometer` provides access to public methods to
use accelerometer of your device.

Simple Examples
---------------

To enable accelerometer::

    >>> from plyer import accelerometer
    >>> accelerometer.enable()

To disable accelerometer::

    >>> accelerometer.disable()

To get the acceleration::

    >>> accelerometer.acceleration
    (-10.048464775085449, 6.825869083404541, 7.7260890007019043)

Supported Plaforms
------------------
Android, iOS, OS X, Linux

'''


class Accelerometer:
    '''
    Accelerometer facade.
    '''

    @property
    def acceleration(self):
        '''
        Property that returns values of the current acceleration
        sensors, as a (x, y, z) tuple. Returns (None, None, None)
        if no data is currently available.
        '''
        return self.get_acceleration()

    def enable(self):
        '''
        Activate the accelerometer sensor. Throws an error if the
        hardware is not available or not implemented on.
        '''
        self._enable()

    def disable(self):
        '''
        Disable the accelerometer sensor.
        '''
        self._disable()

    def get_acceleration(self):
        return self._get_acceleration()

    # private

    def _enable(self):
        raise NotImplementedError()

    def _disable(self):
        raise NotImplementedError()

    def _get_acceleration(self):
        raise NotImplementedError()
