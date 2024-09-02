import time
import threading
from jnius import autoclass

from plyer.facades.audio import Audio

# Recorder Classes
MediaRecorder = autoclass('android.media.MediaRecorder')
AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

# Player Classes
MediaPlayer = autoclass('android.media.MediaPlayer')


class AndroidAudio(Audio):
    '''Audio for android.

    For recording audio we use MediaRecorder Android class.
    For playing audio we use MediaPlayer Android class.
    '''

    def __init__(self, file_path=None):
        default_path = None
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None
        self._check_thread = None
        self._finished_callback = None
        self._format = "opus"
        self.is_playing = False

    def _check_playback(self):
        while self._player and self._player.isPlaying():
            time.sleep(0.25)

        self.is_playing = False
        
        if self._finished_callback and callable(self._finished_callback):
            self._check_thread = None
            self._finished_callback(self)


    def _start(self):
        self._recorder = MediaRecorder()
        if self._format == "aac":
            self._recorder.setAudioSource(AudioSource.DEFAULT)
            self._recorder.setAudioSamplingRate(48000)
            self._recorder.setAudioEncodingBitRate(64000)
            self._recorder.setAudioChannels(1)
            self._recorder.setOutputFormat(OutputFormat.MPEG_4)
            self._recorder.setAudioEncoder(AudioEncoder.AAC)

        else:
            self._recorder.setAudioSource(AudioSource.DEFAULT)
            self._recorder.setAudioSamplingRate(48000)
            self._recorder.setAudioEncodingBitRate(12000)
            self._recorder.setAudioChannels(1)
            self._recorder.setOutputFormat(OutputFormat.OGG)
            self._recorder.setAudioEncoder(AudioEncoder.OPUS)

        self._recorder.setOutputFile(self.file_path)

        self._recorder.prepare()
        self._recorder.start()

    def _stop(self):
        if self._recorder:
            try:
                self._recorder.stop()
                self._recorder.release()
            except Exception as e:
                print("Could not stop recording: "+str(e))

            self._recorder = None

        if self._player:
            try:
                self._player.stop()
                self._player.release()
            except Exception as e:
                print("Could not stop playback: "+str(e))

            self._player = None

        self.is_playing = False

    def _play(self):
        self._player = MediaPlayer()
        self._player.setDataSource(self.file_path)
        self._player.prepare()
        self._player.start()
        self.is_playing = True

        self._check_thread = threading.Thread(target=self._check_playback, daemon=True)
        self._check_thread.start()

    def reload(self):
        self._stop()

    def playing(self):
        return self.is_playing


def instance():
    return AndroidAudio()
