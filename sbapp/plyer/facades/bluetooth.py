'''Bluetooth facade.

Returns the following:

* Bluetooth info

Simple Example
--------------

To get the bluetooth status info::
todo: will be extended to get additional bluetooth info
todo: will be extended to allow bluetooth connections etc.

    >>> from plyer import bluetooth
    >>> bluetooth
    'on' or 'off'

Supported Platforms
-------------------
Android, OS X

'''


class Bluetooth:
    '''
    Bluetooth facade.
    '''

    @property
    def info(self):
        '''
        Property that returns the info (currently status) of the bluetooth.
        '''
        return self.get_info()

    def get_info(self):
        return self._get_info()

    # private

    def _get_info(self, **kwargs):
        raise NotImplementedError()
