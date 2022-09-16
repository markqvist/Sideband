'''
Audio
=====

The :class:`Audio` is used for recording audio.

Default path for recording is set in platform implementation.

.. note::
        On Android the `RECORD_AUDIO`, `WAKE_LOCK` permissions are needed.

Simple Examples
---------------

To get the file path::

    >>> audio.file_path
    '/sdcard/testrecorder.3gp'

To set the file path::

    >>> import os
    >>> current_list = os.listdir('.')
    ['/sdcard/testrecorder.3gp', '/sdcard/testrecorder1.3gp',
    '/sdcard/testrecorder2.3gp', '/sdcard/testrecorder3.3gp']
    >>> file_path = current_list[2]
    >>> audio.file_path = file_path

To start recording::

    >>> from plyer import audio
    >>> audio.start()

To stop recording::

    >>> audio.stop()

To play recording::

    >>> audio.play()

Supported Platforms
-------------------
Android, Windows, macOS

'''


class Audio:
    '''
    Audio facade.
    '''

    state = 'ready'
    _file_path = ''

    def __init__(self, file_path=None):
        super().__init__()
        self._file_path = file_path or self._file_path

    def start(self):
        '''
        Start record.
        '''
        self._start()
        self.state = 'recording'

    def stop(self):
        '''
        Stop record.
        '''
        self._stop()
        self.state = 'ready'

    def play(self):
        '''
        Play current recording.
        '''
        self._play()
        self.state = 'playing'

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, location):
        '''
        Location of the recording.
        '''
        assert isinstance(location, str), 'Location must be string or unicode'
        self._file_path = location

    # private

    def _start(self):
        raise NotImplementedError()

    def _stop(self):
        raise NotImplementedError()

    def _play(self):
        raise NotImplementedError()
