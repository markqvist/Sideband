'''
Screenshot
==========

The :class:`Screenshot` is used for capturing a digital image of what
is currently visible on the monitor.

The default path for taking screenshot is set in each platform implementation.

Simple Examples
---------------

To get the file path::

    >>> screenshot.file_path
    '/sdcard/test.jpg'

To set the file path::

    >>> screenshot.file_path = '/Users/OSXUser/Pictures/screenshot.png'

To take screenshot::

    >>> from plyer import screenshot
    >>> screenshot.capture()
'''


class Screenshot:
    '''
    Screenshot facade.
    '''

    _file_path = ''

    def __init__(self, file_path=None):
        self._file_path = file_path

    def capture(self):
        self._capture()

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, location):
        '''
        Location of the screenshot.
        '''

        self._file_path = location

    # private

    def _capture(self, **kwargs):
        raise NotImplementedError()
