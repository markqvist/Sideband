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
        default_path = '/sdcard/testrecorder.3gp'
        super().__init__(file_path or default_path)

        self._recorder = None
        self._player = None

    def _start(self):
        self._recorder = MediaRecorder()
        self._recorder.setAudioSource(AudioSource.DEFAULT)
        self._recorder.setOutputFormat(OutputFormat.DEFAULT)
        self._recorder.setAudioEncoder(AudioEncoder.DEFAULT)
        self._recorder.setOutputFile(self.file_path)

        self._recorder.prepare()
        self._recorder.start()

    def _stop(self):
        if self._recorder:
            self._recorder.stop()
            self._recorder.release()
            self._recorder = None

        if self._player:
            self._player.stop()
            self._player.release()
            self._player = None

    def _play(self):
        self._player = MediaPlayer()
        self._player.setDataSource(self.file_path)
        self._player.prepare()
        self._player.start()


def instance():
    return AndroidAudio()
