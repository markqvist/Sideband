import copy
import ctypes
from typing import Optional, ByteString, List, Tuple, Callable
import warnings

from . import opus
from .opus_encoder import OpusEncoder
from .pyogg_error import PyOggError

class OpusBufferedEncoder(OpusEncoder):
    # TODO: This could be made more efficient.  We don't need a
    # deque.  Instead, we need only sufficient PCM storage for one
    # whole packet.  We know the size of the packet thanks to
    # set_frame_size().

    def __init__(self) -> None:
        super().__init__()

        self._frame_size_ms: Optional[float] = None
        self._frame_size_bytes: Optional[int] = None

        # Buffer contains the bytes required for the next
        # frame.
        self._buffer: Optional[ctypes.Array] = None

        # Location of the next free byte in the buffer
        self._buffer_index = 0


    def set_frame_size(self, frame_size: float) -> None:
        """ Set the desired frame duration (in milliseconds).

        Valid options are 2.5, 5, 10, 20, 40, or 60ms.

        """

        # Ensure the frame size is valid.  Compare frame size in
        # units of 0.1ms to avoid floating point comparison
        if int(frame_size*10) not in [25, 50, 100, 200, 400, 600]:
            raise PyOggError(
                "Frame size ({:f}) not one of ".format(frame_size)+
                "the acceptable values"
            )

        self._frame_size_ms = frame_size

        self._calc_frame_size()


    def set_sampling_frequency(self, samples_per_second: int) -> None:
        super().set_sampling_frequency(samples_per_second)
        self._calc_frame_size()


    def buffered_encode(self,
                        pcm_bytes: memoryview,
                        flush: bool = False,
                        callback: Callable[[memoryview,int,bool],None] = None
                        ) -> List[Tuple[memoryview, int, bool]]:
        """Gets encoded packets and their number of samples.

        This method returns a list, where each item in the list is
        a tuple.  The first item in the tuple is an Opus-encoded
        frame stored as a bytes-object.  The second item in the
        tuple is the number of samples encoded (excluding
        silence).

        If `callback` is supplied then this method will instead
        return an empty list but call the callback for every
        Opus-encoded frame that would have been returned as a
        list.  This option has the desireable property of
        eliminating the copying of the encoded packets, which is
        required in order to form a list.  The callback should
        take two arguments, the encoded frame (a Python bytes
        object) and the number of samples encoded per channel (an
        int).  The user must either process or copy the data as
        the data may be overwritten once the callback terminates.

        """
        # If there's no work to do return immediately
        if len(pcm_bytes) == 0 and flush == False:
            return [] # no work to do

        # Sanity checks
        if self._frame_size_ms is None:
            raise PyOggError("Frame size must be set before encoding")
        assert self._frame_size_bytes is not None
        assert self._channels is not None
        assert self._buffer is not None
        assert self._buffer_index is not None

        # Local variable initialisation
        results = []
        pcm_index = 0
        pcm_len = len(pcm_bytes)

        # 'Cast' memoryview of PCM to ctypes Array
        Buffer = ctypes.c_ubyte * len(pcm_bytes)
        try:
            pcm_ctypes = Buffer.from_buffer(pcm_bytes)
        except TypeError:
            warnings.warn(
                "Because PCM was read-only, an extra memory "+
                "copy was required; consider storing PCM in "+
                "writable memory (for example, bytearray "+
                "rather than bytes)."
            )
            pcm_ctypes = Buffer.from_buffer(pcm_bytes)
            
        # Either store the encoded packet to return at the end of the
        # method or immediately call the callback with the encoded
        # packet.
        def store_or_callback(encoded_packet: memoryview,
                              samples: int,
                              end_of_stream: bool = False) -> None:
            if callback is None:
                # Store the result
                results.append((
                    encoded_packet,
                    samples,
                    end_of_stream
                ))
            else:
                # Call the callback
                callback(
                    encoded_packet,
                    samples,
                    end_of_stream
                )

        # Fill the remainder of the buffer with silence and encode it.
        # The associated number of samples are only that of actual
        # data, not the added silence.
        def flush_buffer() -> None:
            # Sanity checks to satisfy mypy
            assert self._buffer_index is not None
            assert self._channels is not None
            assert self._buffer is not None
            
            # If the buffer is already empty, we have no work to do
            if self._buffer_index == 0:
                return

            # Store the number of samples currently in the buffer
            samples = (
                self._buffer_index
                // self._channels
                // ctypes.sizeof(opus.opus_int16)
            )

            # Fill the buffer with silence
            ctypes.memset(
                # destination
                ctypes.byref(self._buffer, self._buffer_index),
                # value
                0,
                # count
                len(self._buffer) - self._buffer_index
            )
            
            # Encode the PCM
            # As at 2020-11-05, mypy is unaware that ctype Arrays
            # support the buffer protocol.
            encoded_packet = self.encode(memoryview(self._buffer)) # type: ignore

            # Either store the encoded packet or call the
            # callback
            store_or_callback(encoded_packet, samples, True)

            
        # Copy the data remaining from the provided PCM into the
        # buffer.  Flush if required.
        def copy_insufficient_data() -> None:
            # Sanity checks to satisfy mypy
            assert self._buffer is not None
            
            # Calculate remaining data
            remaining_data = len(pcm_bytes) - pcm_index
                
            # Copy the data into the buffer.
            ctypes.memmove(
                # destination
                ctypes.byref(self._buffer, self._buffer_index),
                # source
                ctypes.byref(pcm_ctypes, pcm_index),
                # count
                remaining_data
            )

            self._buffer_index += remaining_data

            # If we've been asked to flush the buffer then do so
            if flush:
                flush_buffer()
            
        # Loop through the provided PCM and the current buffer,
        # encoding as we have full packets.
        while True:
            # There are two possibilities at this point: either we
            # have previously unencoded data still in the buffer or we
            # do not
            if self._buffer_index == 0:
                # We do not have unencoded data

                # We are free to progress through the PCM that has
                # been provided encoding frames without copying any
                # bytes.  Once there is insufficient data remaining
                # for a complete frame, that data should be copied
                # into the buffer and we have finished.
                if pcm_len - pcm_index > self._frame_size_bytes:
                    # We have enough data remaining in the provided
                    # PCM to encode more than an entire frame without
                    # copying any data.  Unfortunately, splicing a
                    # ctypes array copies the array.  To avoid the
                    # copy we use memoryview see
                    # https://mattgwwalker.wordpress.com/2020/12/12/python-ctypes-slicing/
                    frame_data = memoryview(pcm_bytes)[
                        pcm_index:pcm_index+self._frame_size_bytes
                    ]

                    # Update the PCM index
                    pcm_index += self._frame_size_bytes

                    # Store number of samples (per channel) of actual
                    # data
                    samples = (
                        len(frame_data)
                        // self._channels
                        // ctypes.sizeof(opus.opus_int16)
                    )
                    
                    # Encode the PCM
                    encoded_packet = super().encode(frame_data)

                    # Either store the encoded packet or call the
                    # callback
                    store_or_callback(encoded_packet, samples)

                else:
                    # We do not have enough data to fill a frame while
                    # still having data left over.  Copy the data into
                    # the buffer.
                    copy_insufficient_data()
                    return results

            else:
                # We have unencoded data.

                # Copy the provided PCM into the buffer (up until the
                # buffer is full).  If we can fill it, then we can
                # encode the filled buffer and continue.  If we can't
                # fill it then we've finished.
                data_required = len(self._buffer) - self._buffer_index
                if pcm_len > data_required:
                    # We have sufficient data to fill the buffer and
                    # have data left over.  Copy data into the buffer.
                    assert pcm_index == 0
                    remaining = len(self._buffer) - self._buffer_index
                    ctypes.memmove(
                        # destination
                        ctypes.byref(self._buffer, self._buffer_index),
                        # source
                        pcm_ctypes,
                        # count
                        remaining
                    )
                    pcm_index += remaining
                    self._buffer_index += remaining
                    assert self._buffer_index == len(self._buffer)
                    
                    # Encode the PCM
                    encoded_packet = super().encode(
                        # Memoryviews of ctypes do work, even though
                        # mypy complains.
                        memoryview(self._buffer) # type: ignore
                    )

                    # Store number of samples (per channel) of actual
                    # data
                    samples = (
                        self._buffer_index
                        // self._channels
                        // ctypes.sizeof(opus.opus_int16)
                    )

                    # We've now processed the buffer
                    self._buffer_index = 0
                    
                    # Either store the encoded packet or call the
                    # callback
                    store_or_callback(encoded_packet, samples)
                else:
                    # We have insufficient data to fill the buffer
                    # while still having data left over.  Copy the
                    # data into the buffer.
                    copy_insufficient_data()
                    return results


    def _calc_frame_size(self):
        """Calculates the number of bytes in a frame.

        If the frame size (in milliseconds) and the number of
        samples per seconds have already been specified, then the
        frame size in bytes is set.  Otherwise, this method does
        nothing.

        The frame size is measured in bytes required to store the
        sample.

        """
        if (self._frame_size_ms is None
            or self._samples_per_second is None):
            return

        self._frame_size_bytes = (
            self._frame_size_ms
            * self._samples_per_second
            // 1000
            * ctypes.sizeof(opus.opus_int16)
            * self._channels
        )

        # Allocate space for the buffer
        Buffer = ctypes.c_ubyte * self._frame_size_bytes
        self._buffer = Buffer()


    def _get_next_frame(self, add_silence=False):
        """Gets the next Opus-encoded frame.

        Returns a tuple where the first item is the Opus-encoded
        frame and the second item is the number of encoded samples
        (per channel).

        Returns None if insufficient data is available.

        """
        next_frame = bytes()
        samples = 0

        # Ensure frame size has been specified
        if self._frame_size_bytes is None:
            raise PyOggError(
                "Desired frame size hasn't been set.  Perhaps "+
                "encode() was called before set_frame_size() "+
                "and set_sampling_frequency()?"
            )

        # Check if there's insufficient data in the buffer to fill
        # a frame.
        if self._frame_size_bytes > self._buffer_size:
            if len(self._buffer) == 0:
                # No data at all in buffer
                return None
            if add_silence:
                # Get all remaining data
                while len(self._buffer) != 0:
                    next_frame += self._buffer.popleft()
                self._buffer_size = 0
                # Store number of samples (per channel) of actual
                # data
                samples = (
                    len(next_frame)
                    // self._channels
                    // ctypes.sizeof(opus.opus_int16)
                )
                # Fill remainder of frame with silence
                bytes_remaining = self._frame_size_bytes - len(next_frame)
                next_frame += b'\x00' * bytes_remaining
                return (next_frame, samples)
            else:
                # Insufficient data to fill a frame and we're not
                # adding silence
                return None

        bytes_remaining = self._frame_size_bytes
        while bytes_remaining > 0:
            if len(self._buffer[0]) <= bytes_remaining:
                # Take the whole first item
                buffer_ = self._buffer.popleft()
                next_frame += buffer_
                bytes_remaining -= len(buffer_)
                self._buffer_size -= len(buffer_)
            else:
                # Take only part of the buffer

                # TODO: This could be more efficiently
                # implemented.  Rather than appending back the
                # remaining data, we could just update an index
                # saying where we were up to in regards to the
                # first entry of the buffer.
                buffer_ = self._buffer.popleft()
                next_frame += buffer_[:bytes_remaining]
                self._buffer_size -= bytes_remaining
                # And put the unused part back into the buffer
                self._buffer.appendleft(buffer_[bytes_remaining:])
                bytes_remaining = 0

        # Calculate number of samples (per channel)
        samples = (
            len(next_frame)
            // self._channels
            // ctypes.sizeof(opus.opus_int16)
        )

        return (next_frame, samples)
