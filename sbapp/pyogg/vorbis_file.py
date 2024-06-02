import ctypes

from . import vorbis
from .audio_file import AudioFile
from .pyogg_error import PyOggError

# TODO: Issue #70: Vorbis files with multiple logical bitstreams could
# be supported by chaining VorbisFile instances (with say a 'next'
# attribute that points to the next VorbisFile that would contain the
# PCM for the next logical bitstream).  A considerable constraint to
# implementing this was that examples files that demonstrated multiple
# logical bitstreams couldn't be found or created.  Note that even
# Audacity doesn't handle multiple logical bitstreams (see
# https://wiki.audacityteam.org/wiki/OGG#Importing_multiple_stream_files).

# TODO: Issue #53: Unicode file names are not well supported.
# They may work in macOS and Linux, they don't work under Windows.

class VorbisFile(AudioFile):
    def __init__(self,
                 path: str,
                 bytes_per_sample: int = 2,
                 signed:bool = True) -> None:
        """Load an OggVorbis File.
        
        path specifies the location of the Vorbis file.  Unicode
        filenames may not work correctly under Windows.

        bytes_per_sample specifies the word size of the PCM.  It may
        be either 1 or 2.  Specifying one byte per sample will save
        memory but will likely decrease the quality of the decoded
        audio.

        Only Vorbis files with a single logical bitstream are
        supported.

        """
        # Sanity check the number of bytes per sample
        assert bytes_per_sample==1 or bytes_per_sample==2

        # Sanity check that the vorbis library is available (for mypy)
        assert vorbis.libvorbisfile is not None
        
        #: Bytes per sample
        self.bytes_per_sample = bytes_per_sample

        #: Samples are signed (rather than unsigned)
        self.signed = signed

        # Create a Vorbis File structure
        vf = vorbis.OggVorbis_File()

        # Attempt to open the Vorbis file
        error = vorbis.libvorbisfile.ov_fopen(
            vorbis.to_char_p(path),
            ctypes.byref(vf)
        )

        # Check for errors during opening
        if error != 0:
            raise PyOggError(
                ("File '{}' couldn't be opened or doesn't exist. "+
                 "Error code : {}").format(path, error)
            )

        # Extract info from the Vorbis file
        info = vorbis.libvorbisfile.ov_info(
            ctypes.byref(vf),
            -1 # the current logical bitstream
        )

        #: Number of channels in audio file.
        self.channels = info.contents.channels

        #: Number of samples per second (per channel), 44100 for
        #  example.
        self.frequency = info.contents.rate

        # Extract the total number of PCM samples for the first
        # logical bitstream
        pcm_length_samples = vorbis.libvorbisfile.ov_pcm_total(
            ctypes.byref(vf),
            0 # to extract the length of the first logical bitstream
        )

        # Create a memory block to store the entire PCM
        Buffer = (
            ctypes.c_char
            * (
                pcm_length_samples
                * self.bytes_per_sample
                * self.channels
            )
        )
        self.buffer = Buffer()

        # Create a pointer to the newly allocated memory.  It
        # seems we can only do pointer arithmetic on void
        # pointers.  See
        # https://mattgwwalker.wordpress.com/2020/05/30/pointer-manipulation-in-python/
        buf_ptr = ctypes.cast(
            ctypes.pointer(self.buffer),
            ctypes.c_void_p
        )

        # Storage for the index of the logical bitstream
        bitstream_previous = None 
        bitstream = ctypes.c_int()

        # Set bytes remaining to read into PCM
        read_size = len(self.buffer)

        while True:
            # Convert buffer pointer to the desired type
            ptr = ctypes.cast(
                buf_ptr,
                ctypes.POINTER(ctypes.c_char)
            )

            # Attempt to decode PCM from the Vorbis file
            result = vorbis.libvorbisfile.ov_read(
                ctypes.byref(vf),
                ptr,
                read_size,
                0, # Little endian
                self.bytes_per_sample,
                int(self.signed),
                ctypes.byref(bitstream)
            )

            # Check for errors
            if result < 0:
                raise PyOggError(
                    "An error occurred decoding the Vorbis file: "+
                    f"Error code: {result}"
                )

            # Check that the bitstream hasn't changed as we only
            # support Vorbis files with a single logical bitstream.
            if bitstream_previous is None:
                bitstream_previous = bitstream
            else:
                if bitstream_previous != bitstream:
                    raise PyOggError(
                        "PyOgg currently supports Vorbis files "+
                        "with only one logical stream" 
                    )
                    
            # Check for end of file
            if result == 0:
                break

            # Calculate the number of bytes remaining to read into PCM
            read_size -= result

            # Update the pointer into the buffer
            buf_ptr.value += result
            

        # Close the file and clean up memory
        vorbis.libvorbisfile.ov_clear(ctypes.byref(vf))
