from os.path import join

from pyobjus import autoclass
from pyobjus.dylib_manager import INCLUDE, load_framework

from plyer.facades import Audio
from plyer.platforms.macosx.storagepath import OSXStoragePath

load_framework(INCLUDE.Foundation)
load_framework(INCLUDE.AVFoundation)

AVAudioPlayer = autoclass("AVAudioPlayer")
AVAudioRecorder = autoclass("AVAudioRecorder")
AVAudioFormat = autoclass("AVAudioFormat")
NSString = autoclass('NSString')
NSURL = autoclass('NSURL')
NSError = autoclass('NSError').alloc()


class OSXAudio(Audio):
    def __init__(self, file_path=None):
        default_path = join(
            OSXStoragePath().get_music_dir(),
            'audio.wav'
        )
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._current_file = None

    def _start(self):
        # Conversion of Python file path string to Objective-C NSString
        file_path_NSString = NSString.alloc()
        file_path_NSString = file_path_NSString.initWithUTF8String_(
            self._file_path
        )

        # Definition of Objective-C NSURL object for the output record file
        # specified by NSString file path
        file_NSURL = NSURL.alloc()
        file_NSURL = file_NSURL.initWithString_(file_path_NSString)

        # Internal audio file format specification
        af = AVAudioFormat.alloc()
        af = af.initWithCommonFormat_sampleRate_channels_interleaved_(
            1, 44100.0, 2, True
        )

        # Audio recorder instance initialization with specified file NSURL
        # and audio file format
        self._recorder = AVAudioRecorder.alloc()
        self._recorder = self._recorder.initWithURL_format_error_(
            file_NSURL, af, NSError
        )

        if not self._recorder:
            raise Exception(NSError.code, NSError.domain)

        self._recorder.record()

        # Setting the currently recorded file as current file
        # for using it as a parameter in audio player
        self._current_file = file_NSURL

    def _stop(self):
        if self._recorder:
            self._recorder.stop()
            self._recorder = None

        if self._player:
            self._player.stop()
            self._player = None

    def _play(self):
        # Audio player instance initialization with the file NSURL
        # of the last recorded audio file
        self._player = AVAudioPlayer.alloc()
        self._player = self._player.initWithContentsOfURL_error_(
            self._current_file, NSError
        )

        if not self._player:
            raise Exception(NSError.code, NSError.domain)

        self._player.play()


def instance():
    return OSXAudio()
