'''
Documentation:
http://docs.microsoft.com/en-us/windows/desktop/Multimedia

.. versionadded:: 1.4.0
'''

from os.path import join

from ctypes import windll
from ctypes import (
    sizeof, c_void_p, c_ulonglong, c_ulong,
    c_wchar_p, byref, Structure, create_string_buffer
)
from ctypes.wintypes import DWORD, UINT

from plyer.facades import Audio
from plyer.platforms.win.storagepath import WinStoragePath

# DWORD_PTR i.e. ULONG_PTR, 32/64bit
ULONG_PTR = c_ulonglong if sizeof(c_void_p) == 8 else c_ulong

# device specific symbols
MCI_OPEN = 0x803
MCI_OPEN_TYPE = 0x2000
MCI_OPEN_ELEMENT = 512
MCI_RECORD = 0x80F
MCI_STOP = 0x808
MCI_SAVE = 0x813
MCI_PLAY = 0x806
MCI_CLOSE = 0x804

# recorder specific symbols
MCI_FROM = 4
MCI_TO = 8
MCI_WAIT = 2
MCI_SAVE_FILE = 256


class MCI_OPEN_PARMS(Structure):
    '''
    Struct for MCI_OPEN message parameters.

    .. versionadded:: 1.4.0
    '''

    _fields_ = [
        ('mciOpenParms', ULONG_PTR),
        ('wDeviceID', UINT),
        ('lpstrDeviceType', c_wchar_p),
        ('lpstrElementName', c_wchar_p),
        ('lpstrAlias', c_wchar_p)
    ]


class MCI_RECORD_PARMS(Structure):
    '''
    Struct for MCI_RECORD message parameters.

    http://docs.microsoft.com/en-us/windows/desktop/Multimedia/mci-record-parms

    .. versionadded:: 1.4.0
    '''

    _fields_ = [
        ('dwCallback', ULONG_PTR),
        ('dwFrom', DWORD),
        ('dwTo', DWORD)
    ]


class MCI_SAVE_PARMS(Structure):
    '''
    Struct for MCI_SAVE message parameters.

    http://docs.microsoft.com/en-us/windows/desktop/Multimedia/mci-save-parms

    .. versionadded:: 1.4.0
    '''

    _fields_ = [
        ('dwCallback', ULONG_PTR),
        ('lpfilename', c_wchar_p)
    ]


class MCI_PLAY_PARMS(Structure):
    '''
    Struct for MCI_PLAY message parameters.

    http://docs.microsoft.com/en-us/windows/desktop/Multimedia/mci-play-parms

    .. versionadded:: 1.4.0
    '''

    _fields_ = [
        ('dwCallback', ULONG_PTR),
        ('dwFrom', DWORD),
        ('dwTo', DWORD)
    ]


def send_command(device, msg, flags, params):
    '''
    Generic mciSendCommandW() wrapper with error handler.
    All parameters are required as for mciSendCommandW().
    In case of no `params` passed, use `None`, that value
    won't be dereferenced.

    .. versionadded:: 1.4.0
    '''

    multimedia = windll.winmm
    send_command_w = multimedia.mciSendCommandW
    get_error = multimedia.mciGetErrorStringW

    # error text buffer
    # by API specification 128 is max, however the API sometimes
    # kind of does not respect the documented bounds and returns
    # more characters than buffer length...?!
    error_len = 128

    # big enough to prevent API accidentally segfaulting
    error_text = create_string_buffer(error_len * 2)

    # open a recording device with a new file
    error_code = send_command_w(
        device,  # device ID
        msg,
        flags,

        # reference to parameters structure or original value
        # in case of params=False/0/None/...
        byref(params) if params else params
    )

    # handle error messages if any
    if error_code:
        # device did not open, raise an exception
        get_error(error_code, byref(error_text), error_len)
        error_text = error_text.raw.replace(b'\x00', b'').decode('utf-8')

        # either it can close already open device or it will fail because
        # the device is in non-closable state, but the end result is the same
        # and it makes no sense to parse MCI_CLOSE's error in this case
        send_command_w(device, MCI_CLOSE, 0, None)
        raise Exception(error_code, error_text)

    # return params struct because some commands write into it
    # to pass some values out of the local function scope
    return params


class WinRecorder:
    '''
    Generic wrapper for MCI_RECORD handling the filenames and device closing
    in the same approach like it is used for other platforms.

    .. versionadded:: 1.4.0
    '''

    def __init__(self, device, filename):
        self._device = device
        self._filename = filename

    @property
    def device(self):
        '''
        Public property returning device ID.

        .. versionadded:: 1.4.0
        '''
        return self._device

    @property
    def filename(self):
        '''
        Public property returning filename for current recording.

        .. versionadded:: 1.4.0
        '''
        return self._filename

    def record(self):
        '''
        Start recording a WAV sound.

        .. versionadded:: 1.4.0
        '''
        send_command(
            device=self.device,
            msg=MCI_RECORD,
            flags=0,
            params=None
        )

    def stop(self):
        '''
        Stop recording and save the data to a file path
        self.filename. Wait until the file is written.
        Close the device afterwards.

        .. versionadded:: 1.4.0
        '''

        # stop the recording first
        send_command(
            device=self.device,
            msg=MCI_STOP,
            flags=MCI_WAIT,
            params=None
        )

        # choose filename for the WAV file
        save_params = MCI_SAVE_PARMS()
        save_params.lpfilename = self.filename

        # save the sound data to a file and wait
        # until it ends writing to the file
        send_command(
            device=self.device,
            msg=MCI_SAVE,
            flags=MCI_SAVE_FILE | MCI_WAIT,
            params=save_params
        )

        # close the recording device
        send_command(
            device=self.device,
            msg=MCI_CLOSE,
            flags=0,
            params=None
        )


class WinPlayer:
    '''
    Generic wrapper for MCI_PLAY handling the device closing.

    .. versionadded:: 1.4.0
    '''

    def __init__(self, device):
        self._device = device

    @property
    def device(self):
        '''
        Public property returning device ID.

        .. versionadded:: 1.4.0
        '''
        return self._device

    def play(self):
        '''
        Start playing a WAV sound.

        .. versionadded:: 1.4.0
        '''
        play_params = MCI_PLAY_PARMS()
        play_params.dwFrom = 0

        send_command(
            device=self.device,
            msg=MCI_PLAY,
            flags=MCI_FROM,
            params=play_params
        )

    def stop(self):
        '''
        Stop playing a WAV sound and close the device.

        .. versionadded:: 1.4.0
        '''
        send_command(
            device=self.device,
            msg=MCI_STOP,
            flags=MCI_WAIT,
            params=None
        )

        # close the playing device
        send_command(
            device=self.device,
            msg=MCI_CLOSE,
            flags=0,
            params=None
        )


class WinAudio(Audio):
    '''
    Windows implementation of audio recording and audio playing.

    .. versionadded:: 1.4.0
    '''

    def __init__(self, file_path=None):
        # default path unless specified otherwise
        default_path = join(
            WinStoragePath().get_music_dir(),
            'audio.wav'
        )
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._current_file = None

    def _start(self):
        '''
        Start recording a WAV sound in the background asynchronously.

        .. versionadded:: 1.4.0
        '''

        # clean everything before recording in case
        # there is a different device open
        self._stop()

        # create structure and set device parameters
        open_params = MCI_OPEN_PARMS()
        open_params.lpstrDeviceType = 'waveaudio'
        open_params.lpstrElementName = ''

        # open a new device for recording
        open_params = send_command(
            device=0,  # device ID before opening
            msg=MCI_OPEN,

            # empty filename in lpstrElementName
            # device type in lpstrDeviceType
            flags=MCI_OPEN_ELEMENT | MCI_OPEN_TYPE,
            params=open_params
        )

        # get recorder with device id and path for saving
        self._recorder = WinRecorder(
            device=open_params.wDeviceID,
            filename=self._file_path
        )
        self._recorder.record()

        # Setting the currently recorded file as current file
        # for using it as a parameter in audio player
        self._current_file = self._recorder.filename

    def _stop(self):
        '''
        Stop recording or playing of a WAV sound.

        .. versionadded:: 1.4.0
        '''

        if self._recorder:
            self._recorder.stop()
            self._recorder = None

        if self._player:
            self._player.stop()
            self._player = None

    def _play(self):
        '''
        Play a WAV sound from a file. Prioritize latest recorded file before
        default file path from WinAudio.

        .. versionadded:: 1.4.0
        '''

        # create structure and set device parameters
        open_params = MCI_OPEN_PARMS()
        open_params.lpstrDeviceType = 'waveaudio'
        open_params.lpstrElementName = self._current_file or self._file_path

        # open a new device for playing
        open_params = send_command(
            device=0,  # device ID before opening
            msg=MCI_OPEN,

            # existing filename in lpstrElementName
            # device type in lpstrDeviceType
            flags=MCI_OPEN_ELEMENT | MCI_OPEN_TYPE,
            params=open_params
        )

        # get recorder with device id and path for saving
        self._player = WinPlayer(device=open_params.wDeviceID)
        self._player.play()


def instance():
    '''
    Instance for facade proxy.
    '''
    return WinAudio()
