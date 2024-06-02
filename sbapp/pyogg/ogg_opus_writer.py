import builtins
import copy
import ctypes
import random
import struct
from typing import (
    Optional,
    Union,
    BinaryIO
)

from . import ogg
from . import opus
from .opus_buffered_encoder import OpusBufferedEncoder
#from .opus_encoder import OpusEncoder
from .pyogg_error import PyOggError

class OggOpusWriter():
    """Encodes PCM data into an OggOpus file."""

    def __init__(self, 
                 f: Union[BinaryIO, str],
                 encoder: OpusBufferedEncoder,
                 custom_pre_skip: Optional[int] = None) -> None:
        """Construct an OggOpusWriter.

        f may be either a string giving the path to the file, or
        an already-opened file handle.

        If f is an already-opened file handle, then it is the
        user's responsibility to close the file when they are
        finished with it.  The file should be opened for writing 
        in binary (not text) mode.

        The encoder should be a
        OpusBufferedEncoder and should be fully configured before the
        first call to the `write()` method.

        The Opus encoder requires an amount of "warm up" and when
        stored in an Ogg container that warm up can be skipped.  When
        `custom_pre_skip` is None, the required amount of warm up
        silence is automatically calculated and inserted.  If a custom
        (non-silent) pre-skip is desired, then `custom_pre_skip`
        should be specified as the number of samples (per channel).
        It is then the user's responsibility to pass the non-silent
        pre-skip samples to `encode()`.

        """
        # Store the Opus encoder
        self._encoder = encoder

        # Store the custom pre skip
        self._custom_pre_skip = custom_pre_skip

        # Create a new stream state with a random serial number
        self._stream_state = self._create_stream_state()

        # Create a packet (reused for each pass)
        self._ogg_packet = ogg.ogg_packet()
        self._packet_valid = False

        # Create a page (reused for each pass)
        self._ogg_page = ogg.ogg_page()

        # Counter for the number of packets written into Ogg stream
        self._count_packets = 0

        # Counter for the number of samples encoded into Opus
        # packets
        self._count_samples = 0

        # Flag to indicate if the headers have been written
        self._headers_written = False

        # Flag to indicate that the stream has been finished (the
        # EOS bit was set in a final packet)
        self._finished = False

        # Reference to the current encoded packet (written only
        # when we know if it the last)
        self._current_encoded_packet: Optional[bytes] = None

        # Open file if required.  Given this may raise an exception,
        # it should be the last step of initialisation.
        self._i_opened_the_file = False
        if isinstance(f, str):
            self._file = builtins.open(f, 'wb')
            self._i_opened_the_file = True
        else:
            # Assume it's already opened file
            self._file = f

    def __del__(self) -> None:
        if not self._finished:
            self.close()

    #
    # User visible methods
    #

    def write(self, pcm: memoryview) -> None:
        """Encode the PCM and write out the Ogg Opus stream.

        Encoders the PCM using the provided encoder.

        """
        # Check that the stream hasn't already been finished
        if self._finished:
            raise PyOggError(
                "Stream has already ended.  Perhaps close() was "+
                "called too early?")

        # If we haven't already written out the headers, do so
        # now.  Then, write a frame of silence to warm up the
        # encoder.
        if not self._headers_written:
            pre_skip = self._write_headers(self._custom_pre_skip)
            if self._custom_pre_skip is None:
                self._write_silence(pre_skip)

        # Call the internal method to encode the bytes
        self._write_to_oggopus(pcm)


    def _write_to_oggopus(self, pcm: memoryview, flush: bool = False) -> None:
        assert self._encoder is not None
        
        def handle_encoded_packet(encoded_packet: memoryview,
                                  samples: int,
                                  end_of_stream: bool) -> None:
            # Cast memoryview to ctypes Array
            Buffer = ctypes.c_ubyte * len(encoded_packet)
            encoded_packet_ctypes = Buffer.from_buffer(encoded_packet)

            # Obtain a pointer to the encoded packet
            encoded_packet_ptr = ctypes.cast( 
                encoded_packet_ctypes,
                ctypes.POINTER(ctypes.c_ubyte)
            )

            # Increase the count of the number of samples written
            self._count_samples += samples

            # Place data into the packet
            self._ogg_packet.packet = encoded_packet_ptr
            self._ogg_packet.bytes = len(encoded_packet)
            self._ogg_packet.b_o_s = 0
            self._ogg_packet.e_o_s = end_of_stream
            self._ogg_packet.granulepos = self._count_samples
            self._ogg_packet.packetno = self._count_packets

            # Increase the counter of the number of packets
            # in the stream
            self._count_packets += 1

            # Write the packet into the stream
            self._write_packet()


        # Encode the PCM data into an Opus packet
        self._encoder.buffered_encode(
            pcm,
            flush=flush,
            callback=handle_encoded_packet
        )

    def close(self) -> None:
        # Check we haven't already closed this stream
        if self._finished:
            # We're attempting to close an already closed stream,
            # do nothing more.
            return

        # Flush the underlying buffered encoder
        self._write_to_oggopus(memoryview(bytearray(b"")), flush=True)

        # The current packet must be the end of the stream, update
        # the packet's details
        self._ogg_packet.e_o_s = 1

        # Write the packet to the stream
        if self._packet_valid:
            self._write_packet()

        # Flush the stream of any unwritten pages
        self._flush()

        # Mark the stream as finished
        self._finished = True

        # Close the file if we opened it
        if self._i_opened_the_file:
            self._file.close()
            self._i_opened_the_file = False

        # Clean up the Ogg-related memory
        ogg.ogg_stream_clear(self._stream_state)

        # Clean up the reference to the encoded packet (as it must
        # now have been written)
        del self._current_encoded_packet

    #
    # Internal methods
    #

    def _create_random_serial_no(self) -> ctypes.c_int:
        sizeof_c_int = ctypes.sizeof(ctypes.c_int)
        min_int = -2**(sizeof_c_int*8-1)
        max_int = 2**(sizeof_c_int*8-1)-1
        serial_no = ctypes.c_int(random.randint(min_int, max_int))

        return serial_no

    def _create_stream_state(self) -> ogg.ogg_stream_state:
        # Create a random serial number
        serial_no = self._create_random_serial_no()

        # Create an ogg_stream_state
        ogg_stream_state = ogg.ogg_stream_state()

        # Initialise the stream state
        ogg.ogg_stream_init(
            ctypes.pointer(ogg_stream_state),
            serial_no
        )

        return ogg_stream_state

    def _make_identification_header(self, pre_skip: int, input_sampling_rate: int = 0) -> bytes:
        """Make the OggOpus identification header.

        An input_sampling rate may be set to zero to mean 'unspecified'.

        Only channel mapping family 0 is currently supported.
        This allows mono and stereo signals.

        See https://tools.ietf.org/html/rfc7845#page-12 for more
        details.

        """
        signature = b"OpusHead"
        version = 1
        output_channels = self._encoder._channels
        output_gain = 0
        channel_mapping_family = 0
        data = struct.pack(
            "<BBHIHB",
            version,
            output_channels,
            pre_skip,
            input_sampling_rate,
            output_gain,
            channel_mapping_family
        )

        return signature+data

    def _write_identification_header_packet(self, custom_pre_skip: int) -> int:
        """ Returns pre-skip. """
        if custom_pre_skip is not None:
            # Use the user-specified amount of pre-skip
            pre_skip = custom_pre_skip
        else:
            # Obtain the algorithmic delay of the Opus encoder.  See
            # https://tools.ietf.org/html/rfc7845#page-27
            delay_samples = self._encoder.get_algorithmic_delay()

            # Extra samples are recommended.  See
            # https://tools.ietf.org/html/rfc7845#page-27
            extra_samples = 120

            # We will just fill a whole frame with silence.  Calculate
            # the minimum frame length, which we'll use as the
            # pre-skip.
            frame_durations = [2.5, 5, 10, 20, 40, 60] # milliseconds
            frame_lengths = [
                x * self._encoder._samples_per_second // 1000
                for x in frame_durations
            ]
            for frame_length in frame_lengths:
                if frame_length > delay_samples + extra_samples:
                    pre_skip = frame_length
                    break

        # Create the identification header
        id_header = self._make_identification_header(
            pre_skip = pre_skip
        )

        # Specify the packet containing the identification header
        self._ogg_packet.packet = ctypes.cast(id_header, ogg.c_uchar_p) # type: ignore
        self._ogg_packet.bytes = len(id_header)
        self._ogg_packet.b_o_s = 1
        self._ogg_packet.e_o_s = 0
        self._ogg_packet.granulepos = 0
        self._ogg_packet.packetno = self._count_packets
        self._count_packets += 1

        # Write the identification header
        result = ogg.ogg_stream_packetin(
            self._stream_state,
            self._ogg_packet
        )

        if result != 0:
            raise PyOggError(
                "Failed to write Opus identification header"
            )

        return pre_skip

    def _make_comment_header(self):
        """Make the OggOpus comment header.

        See https://tools.ietf.org/html/rfc7845#page-22 for more
        details.

        """
        signature = b"OpusTags"
        vendor_string = b"ENCODER=PyOgg"
        vendor_string_length = struct.pack("<I",len(vendor_string))
        user_comments_length = struct.pack("<I",0)

        return (
            signature
            + vendor_string_length
            + vendor_string
            + user_comments_length
        )

    def _write_comment_header_packet(self):
        # Specify the comment header
        comment_header = self._make_comment_header()

        # Specify the packet containing the identification header
        self._ogg_packet.packet = ctypes.cast(comment_header, ogg.c_uchar_p)
        self._ogg_packet.bytes = len(comment_header)
        self._ogg_packet.b_o_s = 0
        self._ogg_packet.e_o_s = 0
        self._ogg_packet.granulepos = 0
        self._ogg_packet.packetno = self._count_packets
        self._count_packets += 1

        # Write the header
        result = ogg.ogg_stream_packetin(
            self._stream_state,
            self._ogg_packet
        )

        if result != 0:
            raise PyOggError(
                "Failed to write Opus comment header"
            )

    def _write_page(self):
        """ Write page to file """
        # Cast pointer to ctypes array, which can then be passed to
        # write without issues.
        HeaderBufferPtr = ctypes.POINTER(ctypes.c_ubyte * self._ogg_page.header_len)
        header = HeaderBufferPtr(self._ogg_page.header.contents)[0]
        self._file.write(header)

        BodyBufferPtr = ctypes.POINTER(ctypes.c_ubyte * self._ogg_page.body_len)
        body = BodyBufferPtr(self._ogg_page.body.contents)[0]
        self._file.write(body)

    def _flush(self):
        """ Flush all pages to the file. """
        while ogg.ogg_stream_flush(
                ctypes.pointer(self._stream_state),
                ctypes.pointer(self._ogg_page)) != 0:
            self._write_page()

    def _write_headers(self, custom_pre_skip):
        """ Write the two Opus header packets."""
        pre_skip = self._write_identification_header_packet(
            custom_pre_skip
        )
        self._write_comment_header_packet()

        # Store that the headers have been written
        self._headers_written = True

        # Write out pages to file to ensure that the headers are
        # the only packets to appear on the first page.  If this
        # is not done, the file cannot be read by the library
        # opusfile.
        self._flush()

        return pre_skip

    def _write_packet(self):
        # Place the packet into the stream
        result = ogg.ogg_stream_packetin(
            self._stream_state,
            self._ogg_packet
        )

        # Check for errors
        if result != 0:
            raise PyOggError(
                "Error while placing packet in Ogg stream"
            )

        # Write out pages to file
        while ogg.ogg_stream_pageout(
                ctypes.pointer(self._stream_state),
                ctypes.pointer(self._ogg_page)) != 0:
            self._write_page()

    def _write_silence(self, samples):
        """ Write a frame of silence. """
        silence_length = (
            samples
            * self._encoder._channels
            * ctypes.sizeof(opus.opus_int16)
        )
        silence_pcm = \
            memoryview(bytearray(b"\x00" * silence_length))
        self._write_to_oggopus(silence_pcm)
