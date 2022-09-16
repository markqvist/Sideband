class Light:
    '''Light facade.

    Light sensor measures the ambient light level(illumination) in lx.
    Common uses include controlling screen brightness.

    With method `enable` you can turn on the sensor and
    `disable` method stops the sensor.

    Use property `illumination` to get current illumination in lx.

    .. versionadded:: 1.2.5

    Supported Platforms:: Android
    '''

    @property
    def illumination(self):
        '''Current illumination in lx.'''
        return self._get_illumination()

    def enable(self):
        '''Enable light sensor.'''
        self._enable()

    def disable(self):
        '''Disable light sensor.'''
        self._disable()

    # private

    def _get_illumination(self, **kwargs):
        raise NotImplementedError()

    def _enable(self, **kwargs):
        raise NotImplementedError()

    def _disable(self, **kwargs):
        raise NotImplementedError()
