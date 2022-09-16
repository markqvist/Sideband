class Humidity:
    '''Humidity facade.
       Humidity sensor returns value of humidity.
       With method `enable` you can turn on Humidity sensor and
       'disable' method stops the sensor.
       Use property `tell` to get humidity value.
       
       Supported Platforms
       -------------------
       Android
    '''

    @property
    def tell(self):
        '''Current humidity'''
        return self._get_humidity()

    def enable(self):
        '''Enable Humidity sensor.'''
        self._enable()

    def disable(self):
        '''Disable Humidity sensor.'''
        self._disable()

    # private
    def _get_humidity(self, **kwargs):
        raise NotImplementedError()

    def _enable(self, **kwargs):
        raise NotImplementedError()

    def _disable(self, **kwargs):
        raise NotImplementedError()
