'''
Email
=====

The :class:`Email` provides access to public methods to use email of your
device.

.. note::
    On Android `INTERNET` permission is needed.

Simple Examples
---------------

To send an e-mail::

    >>> from plyer import email
    >>> recipient = 'abc@gmail.com'
    >>> subject = 'Hi'
    >>> text = 'This is an example.'
    >>> create_chooser = False
    >>> email.send(recipient=recipient, subject=subject, text=text,
                   create_chooser=create_chooser)

    >>> # opens email interface where user can change the content.

Supported Platforms
-------------------
Android, iOS, Windows, OS X, Linux

'''


class Email:
    '''
    Email facade.
    '''

    def send(self, recipient=None, subject=None, text=None,
             create_chooser=None):
        '''
        Open an email client message send window, prepopulated with the
        given arguments.

        :param recipient: Recipient of the message (str)
        :param subject: Subject of the message (str)
        :param text: Main body of the message (str)
        :param create_chooser: Whether to display a program chooser to
                               handle the message (bool)

        .. note:: create_chooser is only supported on Android
        '''
        self._send(recipient=recipient, subject=subject, text=text,
                   create_chooser=create_chooser)

    # private

    def _send(self, **kwargs):
        raise NotImplementedError()
