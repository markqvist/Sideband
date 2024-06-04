import time
import threading
import RNS
from sbapp.plyer.facades.audio import Audio
from ffpyplayer.player import MediaPlayer

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
        run = True
        while run and self.sound != None and not self.sound.get_pause():
            time.sleep(0.25)
            if self.duration:
                pts = self.sound.get_pts()
                if pts > self.duration:
                    run = False

        self.is_playing = False
        
        if self._finished_callback and callable(self._finished_callback):
            self._check_thread = None
            self._finished_callback(self)

    def _start(self):
        # TODO: Implement recording
        pass

    def _stop(self):
        if self.sound != None:
            self.sound.set_pause(True)
            self.sound.seek(0, relative=False)
            self.is_playing = False

    def _play(self):
        self.sound = MediaPlayer(self._file_path)
        self.metadata = self.sound.get_metadata()
        self.duration = self.metadata["duration"]
        if self.duration == None:
            time.sleep(0.15)
            self.metadata = self.sound.get_metadata()
            self.duration = self.metadata["duration"]

        RNS.log(str(self.metadata))

        self._loaded_path = self._file_path
        self.is_playing = True

        self._check_thread = threading.Thread(target=self._check_playback, daemon=True)
        self._check_thread.start()

    def reload(self):
        self._loaded_path = None

    def playing(self):
        return self.is_playing


def instance():
    return LinuxAudio()
