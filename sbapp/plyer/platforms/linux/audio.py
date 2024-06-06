import time
import threading
import RNS
import io
from sbapp.plyer.facades.audio import Audio
from ffpyplayer.player import MediaPlayer
from sbapp.pyogg import OpusFile, OpusBufferedEncoder, OggOpusWriter
import pyaudio

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
        self.pa = None
        self.is_playing = False
        self.recorder = None
        self.should_record = False

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

    def _record_job(self):
        samples_per_second = self.default_rate;
        bytes_per_sample = 2; frame_duration_ms = 20
        opus_buffered_encoder = OpusBufferedEncoder()
        opus_buffered_encoder.set_application("voip")
        opus_buffered_encoder.set_sampling_frequency(samples_per_second)
        opus_buffered_encoder.set_channels(1)
        opus_buffered_encoder.set_frame_size(frame_duration_ms)
        ogg_opus_writer = OggOpusWriter(self._file_path, opus_buffered_encoder)

        frame_duration = frame_duration_ms/1000
        frame_size = int(frame_duration * samples_per_second)
        bytes_per_frame = frame_size*bytes_per_sample
        
        read_bytes = 0
        pcm_buf = b""
        should_continue = True
        while self.should_record and self.recorder:
            samples_available = self.recorder.get_read_available()
            bytes_available = samples_available*bytes_per_sample
            if bytes_available > 0:
                read_req = bytes_per_frame - len(pcm_buf)
                read_n = min(bytes_available, read_req)
                read_s = read_n//bytes_per_sample
                rb = self.recorder.read(read_s); read_bytes += len(rb)
                pcm_buf += rb

                if len(pcm_buf) == bytes_per_frame:
                    ogg_opus_writer.write(memoryview(bytearray(pcm_buf)))
                    # RNS.log("Wrote frame of "+str(len(pcm_buf))+", expected size "+str(bytes_per_frame))
                    pcm_buf = b""

        # Finish up anything left in buffer
        time.sleep(frame_duration)
        samples_available = self.recorder.get_read_available()
        bytes_available = samples_available*bytes_per_sample
        if bytes_available > 0:
            read_req = bytes_per_frame - len(pcm_buf)
            read_n = min(bytes_available, read_req)
            read_s = read_n//bytes_per_sample
            rb = self.recorder.read(read_s); read_bytes += len(rb)
            pcm_buf += rb

            if len(pcm_buf) == bytes_per_frame:
                ogg_opus_writer.write(memoryview(bytearray(pcm_buf)))
                # RNS.log("Wrote frame of "+str(len(pcm_buf))+", expected size "+str(bytes_per_frame))
                pcm_buf = b""

        ogg_opus_writer.close()
        if self.recorder:
            self.recorder.close()

    def _start(self):
        self.should_record = True
        if self.pa == None:
            self.pa = pyaudio.PyAudio()
            self.default_input_device = self.pa.get_default_input_device_info()
            self.default_rate = 48000
            # self.default_rate = int(self.default_input_device["defaultSampleRate"])
        if self.recorder:
            self.recorder.close()
            self.recorder = None
        self.recorder = self.pa.open(self.default_rate, 1, pyaudio.paInt16, input=True)
        threading.Thread(target=self._record_job, daemon=True).start()

    def _stop(self):
        if self.should_record == True:
            self.should_record = False

        elif self.sound != None:
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
