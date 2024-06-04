import time
import threading
from sbapp.plyer.facades.audio import Audio
from kivy.core.audio import SoundLoader

class LinuxAudio(Audio):

    def __init__(self, file_path=None):
        default_path = None
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._check_thread = None
        self._finished_callback = None
        self._loaded_path = None
        self.sound = None
        self.is_playing = False

    def _check_playback(self):
        while self.sound != None and self.sound.state == "play":
            time.sleep(0.25)

        self.is_playing = False
        
        if self._finished_callback and callable(self._finished_callback):
            self._check_thread = None
            self._finished_callback(self)

    def _start(self):
        # TODO: Implement recording
        pass

    def _stop(self):
        if self.sound != None and self.sound.state == "play":
            self.sound.stop()
            self.is_playing = False

    def _play(self):
        if self.sound == None or self._loaded_path != self._file_path:
            self.sound = SoundLoader.load(self._file_path)

        self.is_playing = True
        self.sound.play()

        self._check_thread = threading.Thread(target=self._check_playback, daemon=True)
        self._check_thread.start()

    def reload(self):
        self._loaded_path = None
        self.sound = None

    def playing(self):
        return self.is_playing


def instance():
    return LinuxAudio()
