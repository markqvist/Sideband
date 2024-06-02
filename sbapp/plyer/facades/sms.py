'''
Sms
====

The :class:`Sms` provides access to sending Sms from your device.

.. note::

    On Android your app needs the SEND_SMS permission in order to
    send sms messages.

.. versionadded:: 1.2.0

Simple Examples
---------------

To send sms::

    >>> from plyer import sms
    >>> recipient = 9999222299
    >>> message = 'This is an example.'
    >>> sms.send(recipient=recipient, message=message)

Supported Platforms
-------------------
Android, iOS, macOS

'''


class Sms:
    '''
    Sms facade.
    '''

    def send(self, recipient, message, mode=None, **kwargs):
        '''
        Send SMS or open SMS interface.
        Includes optional `mode` parameter for macOS that can be set to
        `'SMS'` if carrier-activated device is correctly paired and
        configured to macOS.

        :param recipient: The receiver
        :param message: the message
        :param mode: (optional, macOS only), can be set to 'iMessage'
        (default) or 'SMS'

        :type recipient: number
        :type message: str
        :type mode: str
        '''
        self._send(recipient=recipient, message=message, mode=mode, **kwargs)

    # private

    def _send(self, **kwargs):
        raise NotImplementedError()
