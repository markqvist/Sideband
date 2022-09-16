class Barometer:
    '''Barometer facade.

    Barometer sensor is used to measure the ambient air pressure in hPa.

    With method `enable` you can turn on pressure sensor and 'disable'
    method stops the sensor.

    Use property `pressure` to get current air pressure in hPa.

    .. versionadded:: 1.2.5

    Supported Platforms:: Android, iOS
    '''

    @property
    def pressure(self):
        '''Current air pressure in hPa.'''
        return self._get_pressure()

    def _get_pressure(self, **kwargs):
        raise NotImplementedError()

    def _enable(self, **kwargs):
        raise NotImplementedError()

    def enable(self):
        '''Enable barometer sensor.'''
        self._enable()

    def _disable(self, **kwargs):
        raise NotImplementedError()

    def disable(self):
        '''Disable barometer sensor.'''
        self._disable()
