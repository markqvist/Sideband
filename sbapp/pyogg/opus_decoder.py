import ctypes

from . import opus
from .pyogg_error import PyOggError

class OpusDecoder:
    def __init__(self):
        self._decoder = None
        self._channels = None
        self._samples_per_second = None
        self._pcm_buffer = None
        self._pcm_buffer_ptr = None
        self._pcm_buffer_size_int = None

    # TODO: Check if there is clean up that we need to do when
    # closing a decoder.

    #
    # User visible methods
    #

    def set_channels(self, n):

        """Set the number of channels.

        n must be either 1 or 2.

        The decoder is capable of filling in either mono or
        interleaved stereo pcm buffers.

        """
        if self._decoder is None:
            if n < 0 or n > 2:
                raise PyOggError(
                    "Invalid number of channels in call to "+
                    "set_channels()"
                )
            self._channels = n
        else:
            raise PyOggError(
                "Cannot change the number of channels after "+
                "the decoder was created.  Perhaps "+
                "set_channels() was called after decode()?"
            )
        self._create_pcm_buffer()

    def set_sampling_frequency(self, samples_per_second):
        """Set the number of samples (per channel) per second.

        samples_per_second must be one of 8000, 12000, 16000,
        24000, or 48000.

        Internally Opus stores data at 48000 Hz, so that should be
        the default value for Fs. However, the decoder can
        efficiently decode to buffers at 8, 12, 16, and 24 kHz so
        if for some reason the caller cannot use data at the full
        sample rate, or knows the compressed data doesn't use the
        full frequency range, it can request decoding at a reduced
        rate.

        """
        if self._decoder is None:
            if samples_per_second in [8000, 12000, 16000, 24000, 48000]:
                self._samples_per_second = samples_per_second
            else:
                raise PyOggError(
                    "Specified sampling frequency "+
                    "({:d}) ".format(samples_per_second)+
                    "was not one of the accepted values"
                )
        else:
            raise PyOggError(
                "Cannot change the sampling frequency after "+
                "the decoder was created.  Perhaps "+
                "set_sampling_frequency() was called after decode()?"
            )
        self._create_pcm_buffer()

    def decode(self, encoded_bytes: memoryview):
        """Decodes an Opus-encoded packet into PCM.

        """
        # If we haven't already created a decoder, do so now
        if self._decoder is None:
            self._decoder = self._create_decoder()

        # Create a ctypes array from the memoryview (without copying
        # data)
        Buffer = ctypes.c_char * len(encoded_bytes)
        encoded_bytes_ctypes = Buffer.from_buffer(encoded_bytes)
            
        # Create pointer to encoded bytes
        encoded_bytes_ptr = ctypes.cast(
            encoded_bytes_ctypes,
            ctypes.POINTER(ctypes.c_ubyte)
        )

        # Store length of encoded bytes into int32
        len_int32 = opus.opus_int32(
            len(encoded_bytes)
        )

        # Check that we have a PCM buffer
        if self._pcm_buffer is None:
            raise PyOggError("PCM buffer was not configured.")

        # Decode the encoded frame
        result = opus.opus_decode(
            self._decoder,
            encoded_bytes_ptr,
            len_int32,
            self._pcm_buffer_ptr,
            self._pcm_buffer_size_int,
            0 # TODO: What's Forward Error Correction about?
        )

        # Check for any errors
        if result < 0:
            raise PyOggError(
                "An error occurred while decoding an Opus-encoded "+
                "packet: "+
                opus.opus_strerror(result).decode("utf")
            )

        # Extract just the valid data as bytes
        end_valid_data = (
            result
            * ctypes.sizeof(opus.opus_int16)
            * self._channels
        )
        
        # Create memoryview of PCM buffer to avoid copying data during slice.
        mv = memoryview(self._pcm_buffer)
        
        # Cast memoryview to chars
        mv = mv.cast('c')
        
        # Slice memoryview to extract only valid data
        mv = mv[:end_valid_data]
        
        return mv


    def decode_missing_packet(self, frame_duration):
        """ Obtain PCM data despite missing a frame.

        frame_duration is in milliseconds.

        """

        # Consider frame duration in units of 0.1ms in order to
        # avoid floating-point comparisons.
        if int(frame_duration*10) not in [25, 50, 100, 200, 400, 600]:
            raise PyOggError(
                "Frame duration ({:f}) is not one of the accepted values".format(frame_duration)
            )

        # Calculate frame size
        frame_size = int(
            frame_duration
            * self._samples_per_second
            // 1000
        )

        # Store frame size as int
        frame_size_int = ctypes.c_int(frame_size)

        # Decode missing packet
        result = opus.opus_decode(
            self._decoder,
            None,
            0,
            self._pcm_buffer_ptr,
            frame_size_int,
            0 # TODO: What is this Forward Error Correction about?
        )

        # Check for any errors
        if result < 0:
            raise PyOggError(
                "An error occurred while decoding an Opus-encoded "+
                "packet: "+
                opus.opus_strerror(result).decode("utf")
            )

        # Extract just the valid data as bytes
        end_valid_data = (
            result
            * ctypes.sizeof(opus.opus_int16)
            * self._channels
        )
        return bytes(self._pcm_buffer)[:end_valid_data]

    #
    # Internal methods
    #

    def _create_pcm_buffer(self):
        if (self._samples_per_second is None
            or self._channels is None):
            # We cannot define the buffer yet
            return

        # Create buffer to hold 120ms of samples.  See "opus_decode()" at
        # https://opus-codec.org/docs/opus_api-1.3.1/group__opus__decoder.html
        max_duration = 120 # milliseconds
        max_samples = max_duration * self._samples_per_second // 1000
        PCMBuffer = opus.opus_int16 * (max_samples * self._channels)
        self._pcm_buffer = PCMBuffer()
        self._pcm_buffer_ptr = (
            ctypes.cast(ctypes.pointer(self._pcm_buffer),
                        ctypes.POINTER(opus.opus_int16))
        )

        # Store samples per channel in an int
        self._pcm_buffer_size_int = ctypes.c_int(max_samples)

    def _create_decoder(self):
        # To create a decoder, we must first allocate resources for it.
        # We want Python to be responsible for the memory deallocation,
        # and thus Python must be responsible for the initial memory
        # allocation.

        # Check that the sampling frequency has been defined
        if self._samples_per_second is None:
            raise PyOggError(
                "The sampling frequency was not specified before "+
                "attempting to create an Opus decoder.  Perhaps "+
                "decode() was called before set_sampling_frequency()?"
            )

        # The sampling frequency must be passed in as a 32-bit int
        samples_per_second = opus.opus_int32(self._samples_per_second)

        # Check that the number of channels has been defined
        if self._channels is None:
            raise PyOggError(
                "The number of channels were not specified before "+
                "attempting to create an Opus decoder.  Perhaps "+
                "decode() was called before set_channels()?"
            )

        # The number of channels must also be passed in as a 32-bit int
        channels = opus.opus_int32(self._channels)

        # Obtain the number of bytes of memory required for the decoder
        size = opus.opus_decoder_get_size(channels);

        # Allocate the required memory for the decoder
        memory = ctypes.create_string_buffer(size)

        # Cast the newly-allocated memory as a pointer to a decoder.  We
        # could also have used opus.od_p as the pointer type, but writing
        # it out in full may be clearer.
        decoder = ctypes.cast(memory, ctypes.POINTER(opus.OpusDecoder))

        # Initialise the decoder
        error = opus.opus_decoder_init(
            decoder,
            samples_per_second,
            channels
        );

        # Check that there hasn't been an error when initialising the
        # decoder
        if error != opus.OPUS_OK:
            raise PyOggError(
                "An error occurred while creating the decoder: "+
                opus.opus_strerror(error).decode("utf")
            )

        # Return our newly-created decoder
        return decoder
