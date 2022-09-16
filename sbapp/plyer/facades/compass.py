'''
Compass
=======

The :class:`Compass` provides access to public methods to use compass of your
device.

Simple Examples
---------------

To enable compass::

    >>> from plyer import compass
    >>> compass.enable()

To disable compass::

    >>> compass.disable()

To get the field::

    >>> compass.field()
    (-23.721826553344727, -5.7114701271057129, -36.749668121337891)

To get the uncalibrated field along with iron bias estimation::

    >>> compass.field_uncalib()
    (a,b,c,x,y,z)
    # a,b,c denote the Geomagnetic field strength
    # (without hard iron calibration) along the three axes.
    # x,y,z denote the Iron bias estimation along the three axes.

Supported Platforms
-------------------
Android, iOS

'''


class Compass:
    '''Compass facade.

    .. versionadded:: 1.2.0
    '''

    @property
    def orientation(self):
        '''
        WARNING:: This property is deprecated after API level 8.
        Use `compass.field` instead.

        Property that returns values of the current compass
        (magnetic field) sensors, as a (x, y, z) tuple.
        Returns (None, None, None) if no data is currently available.
        '''
        return self.get_orientation()

    @property
    def field(self):
        '''
        .. versionadded:: 1.3.1

        Property that returns values of the current compass
        (magnetic field) sensors, as a (x, y, z) tuple.
        Returns (None, None, None) if no data is currently available.
        '''
        return self.get_orientation()

    @property
    def field_uncalib(self):
        '''
        .. versionadded:: 1.3.1

        Property that returns the current value of Uncalibrated Magnetic Field
        (without hard iron calibration) along with the iron bias estimation
        along the three axes.
        '''
        return self.get_field_uncalib()

    def enable(self):
        '''
        Activate the compass sensor.
        '''
        self._enable()

    def disable(self):
        '''
        Disable the compass sensor.
        '''
        self._disable()

    def get_orientation(self):
        return self._get_orientation()

    def get_field_uncalib(self):
        '''
        .. versionadded:: 1.3.1
        '''
        return self._get_field_uncalib()

    # private

    def _enable(self):
        raise NotImplementedError()

    def _disable(self):
        raise NotImplementedError()

    def _get_orientation(self):
        raise NotImplementedError()

    def _get_field_uncalib(self):
        raise NotImplementedError()
