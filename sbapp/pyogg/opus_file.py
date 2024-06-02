import ctypes

from . import ogg
from . import opus
from .pyogg_error import PyOggError
from .audio_file import AudioFile

class OpusFile(AudioFile):
    def __init__(self, path: str) -> None:
        # Open the file
        error = ctypes.c_int()
        of = opus.op_open_file(
            ogg.to_char_p(path),
            ctypes.pointer(error)
        )

        # Check for errors 
        if error.value != 0:
            raise PyOggError(
                ("File '{}' couldn't be opened or doesn't exist. "+
                 "Error code: {}").format(path, error.value)
            )

        # Extract the number of channels in the newly opened file
        #: Number of channels in audio file.
        self.channels = opus.op_channel_count(of, -1)

        # Allocate sufficient memory to store the entire PCM
        pcm_size = opus.op_pcm_total(of, -1)
        Buf = opus.opus_int16*(pcm_size*self.channels)
        buf = Buf()

        # Create a pointer to the newly allocated memory.  It
        # seems we can only do pointer arithmetic on void
        # pointers.  See
        # https://mattgwwalker.wordpress.com/2020/05/30/pointer-manipulation-in-python/
        buf_ptr = ctypes.cast(
            ctypes.pointer(buf),
            ctypes.c_void_p
        )
        assert buf_ptr.value is not None # for mypy
        buf_ptr_zero = buf_ptr.value

        #: Bytes per sample
        self.bytes_per_sample = ctypes.sizeof(opus.opus_int16)

        # Read through the entire file, copying the PCM into the
        # buffer
        samples = 0
        while True:
            # Calculate remaining buffer size
            remaining_buffer = (
                len(buf) # int
                - (buf_ptr.value
                   - buf_ptr_zero) // self.bytes_per_sample
            )

            # Convert buffer pointer to the desired type
            ptr = ctypes.cast(
                buf_ptr,
                ctypes.POINTER(opus.opus_int16)
            )

            # Read the next section of PCM
            ns = opus.op_read(
                of,
                ptr,
                remaining_buffer,
                ogg.c_int_p()
            )

            # Check for errors
            if ns<0:
                raise PyOggError(
                    "Error while reading OggOpus file. "+
                    "Error code: {}".format(ns)
                )

            # Increment the pointer
            buf_ptr.value += (
                ns
                * self.bytes_per_sample
                * self.channels
            )
            assert buf_ptr.value is not None # for mypy

            samples += ns

            # Check if we've finished
            if ns==0:
                break

        # Close the open file
        opus.op_free(of)

        # Opus files are always stored at 48k samples per second
        #: Number of samples per second (per channel).  Always 48,000.
        self.frequency = 48000

        # Cast buffer to a one-dimensional array of chars
        #: Raw PCM data from audio file.
        CharBuffer = (
            ctypes.c_byte
            * (self.bytes_per_sample * self.channels * pcm_size)
        )
        self.buffer = CharBuffer.from_buffer(buf)
