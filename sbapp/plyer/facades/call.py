'''
Call
====

The :class:`Call` provides access to calling feature of your device.

.. note::
    - On Android your app needs the `CALL_PHONE` or `CALL_PRIVILEGED`
    permission in order to make calls.

    - Dialing call feature in not supported yet in iOS devices.

Simple Examples
---------------

To make call::

    >>> from plyer import call
    >>> tel = 9999222299
    >>> call.makecall(tel=tel)

To dial call::

    >>> call.dialcall()

Supported Platforms
-------------------
Android, iOS

'''


class Call:
    '''
    Call facade.
    '''

    def makecall(self, tel):
        '''
        Make calls using your device.

        :param tel: The reciever
        :type tel: number
        '''
        self._makecall(tel=tel)

    def dialcall(self):
        '''
        Opens dialing interface.
        '''
        self._dialcall()

    # private

    def _makecall(self, **kwargs):
        raise NotImplementedError()

    def _dialcall(self, **kwargs):
        raise NotImplementedError()
