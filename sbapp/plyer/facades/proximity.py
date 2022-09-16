class Proximity:
    '''Proximity facade.

    The proximity sensor is commonly used to determine distance whether
    phone is close to your head. Commonly is used when you have a call
    and you stick your phone with your head. Then screen of phone turns off.

    Use method `enable` to turn on proximity sensor and method `disable` for
    turn off.

    To check if some object (or your head) is near sensor check values from
    property `proximity`. It returns `True` when object is close.

    .. versionadded:: 1.2.5

    Supported Platforms::Android
    '''

    @property
    def proximity(self):
        '''Return True or False depending if there is an object or not.

        :return: True if there is an object. Otherwise False.
        '''
        return self._get_proximity()

    def _enable(self, **kwargs):
        raise NotImplementedError()

    def enable(self):
        '''Enable the proximity sensor.
        '''
        self._enable()

    def _disable(self, **kwargs):
        raise NotImplementedError()

    def disable(self):
        '''Disable the proximity sensor.
        '''
        self._disable()

    def _get_proximity(self):
        raise NotImplementedError()
