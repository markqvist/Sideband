from os.path import join

from pyobjus import autoclass
from pyobjus.dylib_manager import INCLUDE, load_framework

from sbapp.plyer.facades import Audio
from sbapp.plyer.platforms.macosx.storagepath import OSXStoragePath

import threading

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
        default_path = None
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._current_file = None

        self._check_thread = None
        self._finished_callback = None
        self._loaded_path = None
        self.is_playing = False
        self.sound = None
        self.pa = None
        self.is_playing = False
        self.recorder = None
        self.should_record = False

    def _check_playback(self):
        while self._player and self._player.isPlaying:
            time.sleep(0.25)
        
        if self._finished_callback and callable(self._finished_callback):
            self._check_thread = None
            self._finished_callback(self)

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
            1, 44100.0, 1, True
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
        # Conversion of Python file path string to Objective-C NSString
        file_path_NSString = NSString.alloc()
        file_path_NSString = file_path_NSString.initWithUTF8String_(
            self._file_path
        )

        # Definition of Objective-C NSURL object for the output record file
        # specified by NSString file path
        file_NSURL = NSURL.alloc()
        file_NSURL = file_NSURL.initWithString_(file_path_NSString)
        self._current_file = file_NSURL

        # Audio player instance initialization with the file NSURL
        # of the last recorded audio file
        self._player = AVAudioPlayer.alloc()
        self._player = self._player.initWithContentsOfURL_error_(
            self._current_file, NSError
        )

        if not self._player:
            raise Exception(NSError.code, NSError.domain)

        self._player.play()

        self._check_thread = threading.Thread(target=self._check_playback, daemon=True)
        self._check_thread.start()

    def reload(self):
        self._loaded_path = None

    def playing(self):
        return self.is_playing


def instance():
    return OSXAudio()
