class Gravity:
    '''Gravity facade.

    .. versionadded:: 1.2.5

    Supported Platforms:: Android

    '''

    @property
    def gravity(self):
        '''Property that returns values of the current gravity force
        as a (x, y, z) tuple. Returns (None, None, None)
        if no data is currently available.
        '''
        return self._get_gravity()

    def enable(self):
        '''Activate the gravity sensor. Throws an error if the
        hardware is not available or not implemented on.
        '''
        self._enable()

    def disable(self):
        '''Disable the gravity sensor.
        '''
        self._disable()

    # private

    def _enable(self):
        raise NotImplementedError()

    def _disable(self):
        raise NotImplementedError()

    def _get_gravity(self):
        raise NotImplementedError()
