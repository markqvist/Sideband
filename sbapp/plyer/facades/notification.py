'''
Notification
============

The :class:`Notification` provides access to public methods to create
notifications.

Simple Examples
---------------

To send notification::

    >>> from plyer import notification
    >>> title = 'plyer'
    >>> message = 'This is an example.'
    >>> notification.notify(title=title, message=message)

Android toast notification::

    >>> from plyer import notification
    >>> notification.notify(message='hello', toast=True)

Android simple notification::

    >>> from plyer import notification
    >>> notification.notify(message='hello', toast=True)

Notification with custom icon::

    >>> from plyer import notification
    >>> notification.notify(title='title', message='hello', app_icon=<path>)

.. versionadded:: 1.0.0

.. versionadded:: 1.4.0
   Add implementation of primitive Android popup-like notification (toast)

.. versionchanged:: 1.4.0
   Android implementation now supports custom icons for notifications.
'''


class Notification:
    '''
    Notification facade.
    '''

    def notify(self, title='', message='', app_name='', app_icon='',
               timeout=10, ticker='', toast=False, hints={}):
        '''
        Send a notification.

        :param title: Title of the notification
        :param message: Message of the notification
        :param app_name: Name of the app launching this notification
        :param app_icon: Icon to be displayed along with the message
        :param timeout: time to display the message for, defaults to 10
        :param ticker: text to display on status bar as the notification
                       arrives
        :param toast: simple Android message instead of full notification
        :param hints: Optional hints that can be used to pass along extra
                      instructions on Linux.
                      (See https://specifications.freedesktop.org/notification-spec/latest/ar01s08.html)  # noqa: E501

        :type title: str
        :type message: str
        :type app_name: str
        :type app_icon: str
        :type timeout: int
        :type ticker: str
        :type toast: bool
        :type hints: dict

        .. note::
           When called on Windows, ``app_icon`` has to be a path to
           a file in .ICO format.

        .. versionadded:: 1.0.0

        .. versionchanged:: 1.4.0
           Add 'toast' keyword argument
        '''

        self._notify(
            title=title, message=message,
            app_icon=app_icon, app_name=app_name,
            timeout=timeout, ticker=ticker, toast=toast, hints=hints
        )

    # private

    def _notify(self, **kwargs):
        raise NotImplementedError("No usable implementation found!")
