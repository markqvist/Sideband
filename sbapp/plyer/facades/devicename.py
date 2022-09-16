'''DeviceName facade.

Returns the following depending on the platform:

* **Android**: Android Device name
* **Linux**: Hostname of the machine
* **OS X**: Hostname of the machine
* **Windows**: Hostname of the machine

Simple Example
--------------

To get the Device Name::

    >>> from plyer import devicename
    >>> devicename.device_name
    'Oneplus 3'

.. versionadded:: 2.1.0
    - first release


Supported Platforms
-------------------
Android, Windows, OS X, Linux

'''


class DeviceName:
    '''
    DeviceName facade.
    '''

    @property
    def device_name(self):
        '''
        Property that returns the device name of the platform.
        '''
        return self._get_device_name()

    # private
    def _get_device_name(self):
        raise NotImplementedError()
