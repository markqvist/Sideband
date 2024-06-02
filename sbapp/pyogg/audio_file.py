from .pyogg_error import PyOggError

class AudioFile:
    """Abstract base class for audio files.

    This class is a base class for audio files (such as Vorbis, Opus,
    and FLAC).  It should not be instatiated directly.
    """

    def __init__(self):
        raise PyOggError("AudioFile is an Abstract Base Class "+
                         "and should not be instantiated") 
    
    def as_array(self):
        """Returns the buffer as a NumPy array.

        The shape of the returned array is in units of (number of
        samples per channel, number of channels).

        The data type is either 8-bit or 16-bit signed integers,
        depending on bytes_per_sample.

        The buffer is not copied, but rather the NumPy array
        shares the memory with the buffer.

        """
        # Assumes that self.buffer is a one-dimensional array of
        # bytes and that channels are interleaved.
        
        import numpy # type: ignore
        
        assert self.buffer is not None
        assert self.channels is not None

        # The following code assumes that the bytes in the buffer
        # represent 8-bit or 16-bit signed ints.  Ensure the number of
        # bytes per sample matches that assumption.
        assert self.bytes_per_sample == 1 or self.bytes_per_sample == 2

        # Create a dictionary mapping bytes per sample to numpy data
        # types
        dtype = {
            1: numpy.int8,
            2: numpy.int16
        }
        
        # Convert the ctypes buffer to a NumPy array
        array = numpy.frombuffer(
            self.buffer,
            dtype=dtype[self.bytes_per_sample]
        )

        # Reshape the array
        return array.reshape(
            (len(self.buffer)
             // self.bytes_per_sample
             // self.channels,
             self.channels)
        )
