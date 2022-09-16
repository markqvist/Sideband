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
Android, iOS

'''


class Sms:
    '''
    Sms facade.
    '''

    def send(self, recipient, message):
        '''
        Send SMS or open SMS interface.

        :param recipient: The receiver
        :param message: the message

        :type recipient: number
        :type message: str
        '''
        self._send(recipient=recipient, message=message)

    # private

    def _send(self, **kwargs):
        raise NotImplementedError()
