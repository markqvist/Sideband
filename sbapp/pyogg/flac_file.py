import ctypes
from itertools import chain

from . import flac
from .audio_file import AudioFile
from .pyogg_error import PyOggError

def _to_char_p(string):
    try:
        return ctypes.c_char_p(string.encode("utf-8"))
    except:
        return ctypes.c_char_p(string)

def _resize_array(array, new_size):
    return (array._type_*new_size).from_address(ctypes.addressof(array))


class FlacFile(AudioFile):
    def write_callback(self, decoder, frame, buffer, client_data):
        multi_channel_buf = _resize_array(buffer.contents, self.channels)
        arr_size = frame.contents.header.blocksize
        if frame.contents.header.channels >= 2:
            arrays = []
            for i in range(frame.contents.header.channels):
                arr = ctypes.cast(multi_channel_buf[i], ctypes.POINTER(flac.FLAC__int32*arr_size)).contents
                arrays.append(arr[:])

            arr = list(chain.from_iterable(zip(*arrays)))

            self.buffer[self.buffer_pos : self.buffer_pos + len(arr)] = arr[:]
            self.buffer_pos += len(arr)

        else:
            arr = ctypes.cast(multi_channel_buf[0], ctypes.POINTER(flac.FLAC__int32*arr_size)).contents
            self.buffer[self.buffer_pos : self.buffer_pos + arr_size] = arr[:]
            self.buffer_pos += arr_size
        return 0

    def metadata_callback(self,decoder, metadata, client_data):
        if not self.buffer:
            self.total_samples = metadata.contents.data.stream_info.total_samples
            self.channels = metadata.contents.data.stream_info.channels
            Buffer = flac.FLAC__int16*(self.total_samples * self.channels)
            self.buffer = Buffer()
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

        #: Raw PCM data from audio file.
        self.buffer = None

        self.buffer_pos = 0

        write_callback_ = flac.FLAC__StreamDecoderWriteCallback(self.write_callback)

        metadata_callback_ = flac.FLAC__StreamDecoderMetadataCallback(self.metadata_callback)

        error_callback_ = flac.FLAC__StreamDecoderErrorCallback(self.error_callback)

        init_status = flac.FLAC__stream_decoder_init_file(
            self.decoder,
            _to_char_p(path), # This will have an issue with Unicode filenames
            write_callback_,
            metadata_callback_,
            error_callback_,
            self.client_data
        )

        if init_status: # error
            error = flac.FLAC__StreamDecoderInitStatusEnum[init_status]
            raise PyOggError(
                "An error occured when trying to open '{}': {}".format(path, error)
            )

        metadata_status = (flac.FLAC__stream_decoder_process_until_end_of_metadata(self.decoder))
        if not metadata_status: # error
            raise PyOggError("An error occured when trying to decode the metadata of {}".format(path))

        stream_status = (flac.FLAC__stream_decoder_process_until_end_of_stream(self.decoder))
        if not stream_status: # error
            raise PyOggError("An error occured when trying to decode the audio stream of {}".format(path))

        flac.FLAC__stream_decoder_finish(self.decoder)

        #: Length of buffer
        self.buffer_length = len(self.buffer)

        self.bytes_per_sample = ctypes.sizeof(flac.FLAC__int16) # See definition of Buffer in metadata_callback()

        # Cast buffer to one-dimensional array of chars
        CharBuffer = (
            ctypes.c_byte *
            (self.bytes_per_sample * len(self.buffer))
        )
        self.buffer = CharBuffer.from_buffer(self.buffer) 

        # FLAC audio is always signed.  See
        # https://xiph.org/flac/api/group__flac__stream__decoder.html#gaf98a4f9e2cac5747da6018c3dfc8dde1
        self.signed = True
