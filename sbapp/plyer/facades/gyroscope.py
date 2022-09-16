'''
Gyroscope
============

The gyroscope measures the rate of rotation around a device's x, y,
and z axis.

The :class:`Gyroscope` provides access to public methods to
use gyroscope of your device.

Simple Examples
---------------

To enable gyroscope::

    >>> from plyer import gyroscope
    >>> gyroscope.enable()

To disable gyroscope::

    >>> gyroscope.disable()

To get the rate of rotation along the three axes::

    >>> gyroscope.rotation
    (-0.0034587313421070576, -0.0073830625042319298, 0.0046892408281564713)

To get the uncalibrated rate of rotation along the three axes along with the
drift compensation::

    >>> gyroscope.rotation_uncalib
    ()
    where the first three values show the rate of rotation w/o drift
    compensation and the last three show the estimated drift along the three
    axes.

Supported Platforms
-------------------
Android, iOS

'''


class Gyroscope:
    '''
    Gyroscope facade.

    .. versionadded:: 1.3.1
    '''

    @property
    def rotation(self):
        '''
        Property that returns the rate of rotation around the device's local
        X, Y and Z axis.

        Along x-axis: angular speed around the X axis
        Along y-axis: angular speed around the Y axis
        Along z-axis: angular speed around the Z axis

        Returns (None, None, None) if no data is currently available.
        '''
        return self.get_orientation()

    @property
    def rotation_uncalib(self):
        '''
        Property that returns the current rate of rotation around the X, Y and
        Z axis. An estimation of the drift on each axis is reported as well.

        Along x-axis: angular speed (w/o drift compensation) around the X axis
        Along y-axis: angular speed (w/o drift compensation) around the Y axis
        Along z-axis: angular speed (w/o drift compensation) around the Z axis

        Along x-axis: estimated drift around X axis
        Along y-axis: estimated drift around Y axis
        Along z-axis: estimated drift around Z axis

        Returns (None, None, None, None, None, None) if no data is currently
        available.
        '''
        return self.get_rotation_uncalib()

    @property
    def orientation(self):
        '''
        WARNING:: This property is deprecated after API Level 8.
        Use `gyroscope.rotation` instead.

        Property that returns values of the current Gyroscope sensors, as
        a (x, y, z) tuple. Returns (None, None, None) if no data is currently
        available.
        '''
        return self.get_orientation()

    def enable(self):
        '''
        Activate the Gyroscope sensor.
        '''
        self._enable()

    def disable(self):
        '''
        Disable the Gyroscope sensor.
        '''
        self._disable()

    def get_orientation(self):
        return self._get_orientation()

    def get_rotation_uncalib(self):
        return self._get_rotation_uncalib()

    # private

    def _enable(self):
        raise NotImplementedError()

    def _disable(self):
        raise NotImplementedError()

    def _get_orientation(self):
        raise NotImplementedError()

    def _get_rotation_uncalib(self):
        raise NotImplementedError()
