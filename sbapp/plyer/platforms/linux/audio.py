import time
import threading
from sbapp.plyer.facades.audio import Audio

class LinuxAudio(Audio):

    def __init__(self, file_path=None):
        default_path = None
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._check_thread = None
        self._finished_callback = None

    def _check_playback(self):
        while self.is_playing:
            time.sleep(0.25)
        
        if self._finished_callback and callable(self._finished_callback):
            self._check_thread = None
            self._finished_callback(self)

    def _start(self):
        # TODO: Implement recording
        pass

    def _stop(self):
        # TODO: Implement recording
        pass

    def _play(self):
        # TODO: Implement playback
        self.is_playing = True

        self._check_thread = threading.Thread(target=self._check_playback, daemon=True)
        self._check_thread.start()

        def fauxplay():
            time.sleep(1.5)
            self.is_playing = False

        threading.Thread(target=fauxplay, daemon=True).start()



def instance():
    return LinuxAudio()
