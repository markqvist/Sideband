import ctypes

from . import vorbis
from .pyogg_error import PyOggError

class VorbisFileStream:
    def __init__(self, path, buffer_size=8192):
        self.exists = False
        self._buffer_size = buffer_size
        
        self.vf = vorbis.OggVorbis_File()
        error = vorbis.ov_fopen(path, ctypes.byref(self.vf))
        if error != 0:
            raise PyOggError("file couldn't be opened or doesn't exist. Error code : {}".format(error))

        info = vorbis.ov_info(ctypes.byref(self.vf), -1)

        #: Number of channels in audio file.
        self.channels = info.contents.channels

        #: Number of samples per second (per channel).  Always
        #  48,000.
        self.frequency = info.contents.rate

        array = (ctypes.c_char*(self._buffer_size*self.channels))()

        self.buffer_ = ctypes.cast(ctypes.pointer(array), ctypes.c_char_p)

        self.bitstream = ctypes.c_int()
        self.bitstream_pointer = ctypes.pointer(self.bitstream)

        self.exists = True # TODO: is this the best place for this statement?

        #: Bytes per sample
        self.bytes_per_sample = 2 # TODO: Where is this defined?

    def __del__(self):
        if self.exists:
            vorbis.ov_clear(ctypes.byref(self.vf))
        self.exists = False

    def clean_up(self):
        vorbis.ov_clear(ctypes.byref(self.vf))

        self.exists = False

    def get_buffer(self):
        """get_buffer() -> bytesBuffer, bufferLength

        Returns None when all data has been read from the file.

        """
        if not self.exists:
            return None
        buffer = []
        total_bytes_written = 0

        while True:
            new_bytes = vorbis.ov_read(ctypes.byref(self.vf), self.buffer_, self._buffer_size*self.channels - total_bytes_written, 0, 2, 1, self.bitstream_pointer)

            array_ = ctypes.cast(self.buffer_, ctypes.POINTER(ctypes.c_char*(self._buffer_size*self.channels))).contents

            buffer.append(array_.raw[:new_bytes])

            total_bytes_written += new_bytes

            if new_bytes == 0 or total_bytes_written >= self._buffer_size*self.channels:
                break

        out_buffer = b"".join(buffer)

        if total_bytes_written == 0:
            self.clean_up()
            return(None)

        return out_buffer

    def get_buffer_as_array(self):
        """Provides the buffer as a NumPy array.

        Note that the underlying data type is 16-bit signed
        integers.

        Does not copy the underlying data, so the returned array
        should either be processed or copied before the next call
        to get_buffer() or get_buffer_as_array().

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
