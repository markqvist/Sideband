import ctypes
from itertools import chain

from . import flac
from .pyogg_error import PyOggError

def _to_char_p(string):
    try:
        return ctypes.c_char_p(string.encode("utf-8"))
    except:
        return ctypes.c_char_p(string)

def _resize_array(array, new_size):
    return (array._type_*new_size).from_address(ctypes.addressof(array))


class FlacFileStream:
    def write_callback(self,decoder, frame, buffer, client_data):
        multi_channel_buf = _resize_array(buffer.contents, self.channels)
        arr_size = frame.contents.header.blocksize
        if frame.contents.header.channels >= 2:
            arrays = []
            for i in range(frame.contents.header.channels):
                arr = ctypes.cast(multi_channel_buf[i], ctypes.POINTER(flac.FLAC__int32*arr_size)).contents
                arrays.append(arr[:])

            arr = list(chain.from_iterable(zip(*arrays)))

            self.buffer = (flac.FLAC__int16*len(arr))(*arr)
            self.bytes_written = len(arr) * 2

        else:
            arr = ctypes.cast(multi_channel_buf[0], ctypes.POINTER(flac.FLAC__int32*arr_size)).contents
            self.buffer = (flac.FLAC__int16*len(arr))(*arr[:])
            self.bytes_written = arr_size * 2
        return 0

    def metadata_callback(self,decoder, metadata, client_data):
        self.total_samples = metadata.contents.data.stream_info.total_samples
        self.channels = metadata.contents.data.stream_info.channels
        self.frequency = metadata.contents.data.stream_info.sample_rate

    def error_callback(self,decoder, status, client_data):
        raise PyOggError("An error occured during the process of decoding. Status enum: {}".format(flac.FLAC__StreamDecoderErrorStatusEnum[status]))

    def __init__(self, path):
        self.decoder = flac.FLAC__stream_decoder_new()

        self.client_data = ctypes.c_void_p()

        #: Number of channels in audio file.
        self.channels = None

        #: Number of samples per second (per channel).  For
        #  example, 44100.
        self.frequency = None

        self.total_samples = None

        self.buffer = None

        self.bytes_written = None

        self.write_callback_ = flac.FLAC__StreamDecoderWriteCallback(self.write_callback)

        self.metadata_callback_ = flac.FLAC__StreamDecoderMetadataCallback(self.metadata_callback)

        self.error_callback_ = flac.FLAC__StreamDecoderErrorCallback(self.error_callback)

        init_status = flac.FLAC__stream_decoder_init_file(self.decoder,
                                      _to_char_p(path),
                                      self.write_callback_,
                                      self.metadata_callback_,
                                      self.error_callback_,
                                      self.client_data)

        if init_status: # error
            raise PyOggError("An error occured when trying to open '{}': {}".format(path, flac.FLAC__StreamDecoderInitStatusEnum[init_status]))

        metadata_status = (flac.FLAC__stream_decoder_process_until_end_of_metadata(self.decoder))
        if not metadata_status: # error
            raise PyOggError("An error occured when trying to decode the metadata of {}".format(path))

        #: Bytes per sample
        self.bytes_per_sample = 2

    def get_buffer(self):
        """Returns the buffer.

        Returns buffer (a bytes object) or None if all data has
        been read from the file.

        """
        # Attempt to read a single frame of audio
        stream_status = (flac.FLAC__stream_decoder_process_single(self.decoder))
        if not stream_status: # error
            raise PyOggError("An error occured when trying to decode the audio stream of {}".format(path))

        # Check if we encountered the end of the stream
        if (flac.FLAC__stream_decoder_get_state(self.decoder) == 4): # end of stream
            return None

        buffer_as_bytes = bytes(self.buffer)
        return buffer_as_bytes

    def clean_up(self):
        flac.FLAC__stream_decoder_finish(self.decoder)

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
