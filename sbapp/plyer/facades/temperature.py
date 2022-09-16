# coding=utf-8


class Temperature:
    '''Temperature facade.

    Temperature sensor is used to measure the ambient room temperature in
    degrees Celsius (°C)
    With method `enable` you can turn on temperature sensor and 'disable'
    method stops the sensor.
    Use property `temperature` to get ambient air temperature in degree C.

    .. versionadded:: 1.2.5

    Supported Platforms:: Android

    '''

    @property
    def temperature(self):
        '''Current air temperature in degree C.'''
        return self._get_temperature()

    def enable(self):
        '''Enable temperature sensor.'''
        self._enable()

    def disable(self):
        '''Disable temperature sensor.'''
        self._disable()

    # private

    def _get_temperature(self, **kwargs):
        raise NotImplementedError()

    def _enable(self, **kwargs):
        raise NotImplementedError()

    def _disable(self, **kwargs):
        raise NotImplementedError()
