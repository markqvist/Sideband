import ctypes

from . import ogg
from . import opus
from .pyogg_error import PyOggError

class OpusFileStream:
    def __init__(self, path):
        """Opens an OggOpus file as a stream.

        path should be a string giving the filename of the file to
        open.  Unicode file names may not work correctly.

        An exception will be raised if the file cannot be opened
        correctly.

        """ 
        error = ctypes.c_int()

        self.of = opus.op_open_file(ogg.to_char_p(path), ctypes.pointer(error))

        if error.value != 0:
            self.of = None
            raise PyOggError("file couldn't be opened or doesn't exist. Error code : {}".format(error.value))

        #: Number of channels in audio file
        self.channels = opus.op_channel_count(self.of, -1)

        #: Total PCM Length
        self.pcm_size = opus.op_pcm_total(self.of, -1)

        #: Number of samples per second (per channel)
        self.frequency = 48000

        # The buffer size should be (per channel) large enough to
        # hold 120ms (the largest possible Opus frame) at 48kHz.
        # See https://opus-codec.org/docs/opusfile_api-0.7/group__stream__decoding.html#ga963c917749335e29bb2b698c1cb20a10
        self.buffer_size = self.frequency // 1000 * 120 * self.channels
        self.Buf = opus.opus_int16 * self.buffer_size
        self._buf = self.Buf()
        self.buffer_ptr = ctypes.cast(
            ctypes.pointer(self._buf),
            opus.opus_int16_p
        )

        #: Bytes per sample
        self.bytes_per_sample = ctypes.sizeof(opus.opus_int16)

    def __del__(self):
        if self.of is not None:
            opus.op_free(self.of)

    def get_buffer(self):
        """Obtains the next frame of PCM samples.

        Returns an array of signed 16-bit integers.  If the file
        is in stereo, the left and right channels are interleaved.

        Returns None when all data has been read.

        The array that is returned should be either processed or
        copied before the next call to :meth:`~get_buffer` or
        :meth:`~get_buffer_as_array` as the array's memory is reused for
        each call.

        """
        # Read the next frame
        samples_read = opus.op_read(
            self.of,
            self.buffer_ptr,
            self.buffer_size,
            None
        )

        # Check for errors
        if samples_read < 0:
            raise PyOggError(
                "Failed to read OpusFileStream.  Error {:d}".format(samples_read)
            )

        # Check if we've reached the end of the stream
        if samples_read == 0:
            return None

        # Cast the pointer to opus_int16 to an array of the
        # correct size
        result_ptr = ctypes.cast(
            self.buffer_ptr,
            ctypes.POINTER(opus.opus_int16 * (samples_read*self.channels))
        )

        # Convert the array to Python bytes
        return bytes(result_ptr.contents)

    def get_buffer_as_array(self):
        """Provides the buffer as a NumPy array.

        Note that the underlying data type is 16-bit signed
        integers.

        Does not copy the underlying data, so the returned array
        should either be processed or copied before the next call
        to :meth:`~get_buffer` or :meth:`~get_buffer_as_array`.

        """
        import numpy # type: ignore

        # Read the next samples from the stream
        buf = self.get_buffer()

        # Check if we've come to the end of the stream
        if buf is None:
            return None

        # Convert the bytes buffer to a NumPy array
        array = numpy.frombuffer(
            buf,
            dtype=numpy.int16
        )

        # Reshape the array
        return array.reshape(
            (len(buf)
             // self.bytes_per_sample
             // self.channels,
             self.channels)
        )
