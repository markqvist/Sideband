import ctypes

from .pyogg_error import PyOggError
from .ogg import PYOGG_OGG_AVAIL
from .vorbis import PYOGG_VORBIS_AVAIL, PYOGG_VORBIS_FILE_AVAIL, PYOGG_VORBIS_ENC_AVAIL
from .opus import PYOGG_OPUS_AVAIL, PYOGG_OPUS_FILE_AVAIL, PYOGG_OPUS_ENC_AVAIL
from .flac import PYOGG_FLAC_AVAIL


#: PyOgg version number.  Versions should comply with PEP440.
__version__ = '0.7'


if (PYOGG_OGG_AVAIL and PYOGG_VORBIS_AVAIL and PYOGG_VORBIS_FILE_AVAIL):
    # VorbisFile
    from .vorbis_file import VorbisFile
    # VorbisFileStream
    from .vorbis_file_stream import VorbisFileStream

else:
    class VorbisFile: # type: ignore
        def __init__(*args, **kw):
            if not PYOGG_OGG_AVAIL:
                raise PyOggError("The Ogg library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            raise PyOggError("The Vorbis libraries weren't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")

    class VorbisFileStream: # type: ignore
        def __init__(*args, **kw):
            if not PYOGG_OGG_AVAIL:
                raise PyOggError("The Ogg library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            raise PyOggError("The Vorbis libraries weren't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")



if (PYOGG_OGG_AVAIL and PYOGG_OPUS_AVAIL and PYOGG_OPUS_FILE_AVAIL):
    # OpusFile
    from .opus_file import OpusFile
    # OpusFileStream
    from .opus_file_stream import OpusFileStream

else:
    class OpusFile: # type: ignore
        def __init__(*args, **kw):
            if not PYOGG_OGG_AVAIL:
                raise PyOggError("The Ogg library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            if not PYOGG_OPUS_AVAIL:
                raise PyOggError("The Opus library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            if not PYOGG_OPUS_FILE_AVAIL:
                raise PyOggError("The OpusFile library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            raise PyOggError("Unknown initialisation error")

    class OpusFileStream: # type: ignore
        def __init__(*args, **kw):
            if not PYOGG_OGG_AVAIL:
                raise PyOggError("The Ogg library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            if not PYOGG_OPUS_AVAIL:
                raise PyOggError("The Opus library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            if not PYOGG_OPUS_FILE_AVAIL:
                raise PyOggError("The OpusFile library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            raise PyOggError("Unknown initialisation error")


if PYOGG_OPUS_AVAIL:
    # OpusEncoder
    from .opus_encoder import OpusEncoder
    # OpusBufferedEncoder
    from .opus_buffered_encoder import OpusBufferedEncoder
    # OpusDecoder
    from .opus_decoder import OpusDecoder

else:
    class OpusEncoder: # type: ignore
        def __init__(*args, **kw):
            raise PyOggError("The Opus library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")

    class OpusBufferedEncoder: # type: ignore
        def __init__(*args, **kw):
            raise PyOggError("The Opus library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
        
    class OpusDecoder: # type: ignore
        def __init__(*args, **kw):
            raise PyOggError("The Opus library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")

if (PYOGG_OGG_AVAIL and PYOGG_OPUS_AVAIL):        
    # OggOpusWriter
    from .ogg_opus_writer import OggOpusWriter
    
else:
    class OggOpusWriter: # type: ignore
        def __init__(*args, **kw):
            if not PYOGG_OGG_AVAIL:
                raise PyOggError("The Ogg library wasn't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
            raise PyOggError("The Opus library was't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
        

if PYOGG_FLAC_AVAIL:
    # FlacFile
    from .flac_file import FlacFile
    # FlacFileStream
    from .flac_file_stream import FlacFileStream
else:
    class FlacFile: # type: ignore
        def __init__(*args, **kw):
            raise PyOggError("The FLAC libraries weren't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")

    class FlacFileStream: # type: ignore
        def __init__(*args, **kw):
            raise PyOggError("The FLAC libraries weren't found or couldn't be loaded (maybe you're trying to use 64bit libraries with 32bit Python?)")
