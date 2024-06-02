############################################################
# Vorbis license:                                          #
############################################################
"""
Copyright (c) 2002-2015 Xiph.org Foundation

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of the Xiph.org Foundation nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import ctypes
import ctypes.util
from traceback import print_exc as _print_exc
import os

OV_EXCLUDE_STATIC_CALLBACKS = False

__MINGW32__ = False

_WIN32 = False

from .ogg import *

from .library_loader import ExternalLibrary, ExternalLibraryError

__here = os.getcwd()

libvorbis = None

try:
    names = {
        "Windows": "libvorbis.dll",
        "Darwin": "libvorbis.0.dylib",
        "external": "vorbis"
    }
    libvorbis = Library.load(names, tests = [lambda lib: hasattr(lib, "vorbis_info_init")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

libvorbisfile = None

try:
    names = {
        "Windows": "libvorbisfile.dll",
        "Darwin": "libvorbisfile.3.dylib",
        "external": "vorbisfile"
    }
    libvorbisfile = Library.load(names, tests = [lambda lib: hasattr(lib, "ov_clear")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

libvorbisenc = None

# In some cases, libvorbis may also have the libvorbisenc functionality.
libvorbis_is_also_libvorbisenc = True

for f in ("vorbis_encode_ctl",
          "vorbis_encode_init",
          "vorbis_encode_init_vbr",
          "vorbis_encode_setup_init",
          "vorbis_encode_setup_managed",
          "vorbis_encode_setup_vbr"):
    if not hasattr(libvorbis, f):
        libvorbis_is_also_libvorbisenc = False
        break

if libvorbis_is_also_libvorbisenc:
    libvorbisenc = libvorbis
else:
    try:
        names = {
            "Windows": "libvorbisenc.dll",
            "Darwin": "libvorbisenc.2.dylib",
            "external": "vorbisenc"
        }
        libvorbisenc = Library.load(names, tests = [lambda lib: hasattr(lib, "vorbis_encode_init")])
    except ExternalLibraryError:
        pass
    except:
        _print_exc()

if libvorbis is None:
    PYOGG_VORBIS_AVAIL = False
else:
    PYOGG_VORBIS_AVAIL = True

if libvorbisfile is None:
    PYOGG_VORBIS_FILE_AVAIL = False
else:
    PYOGG_VORBIS_FILE_AVAIL = True

if libvorbisenc is None:
    PYOGG_VORBIS_ENC_AVAIL = False
else:
    PYOGG_VORBIS_ENC_AVAIL = True

# FIXME: What's the story with the lack of checking for PYOGG_VORBIS_ENC_AVAIL?
# We just seem to assume that it's available.

if PYOGG_OGG_AVAIL and PYOGG_VORBIS_AVAIL and PYOGG_VORBIS_FILE_AVAIL:
    # Sanity check also satisfies mypy type checking
    assert libogg is not None
    assert libvorbis is not None
    assert libvorbisfile is not None


    # codecs
    class vorbis_info(ctypes.Structure):
        """
        Wrapper for:
            typedef struct vorbis_info vorbis_info;
        """
        _fields_ = [("version", c_int),
                    ("channels", c_int),
                    ("rate", c_long),

                    ("bitrate_upper", c_long),
                    ("bitrate_nominal", c_long),
                    ("bitrate_lower", c_long),
                    ("bitrate_window", c_long),
                    ("codec_setup", c_void_p)]



    class vorbis_dsp_state(ctypes.Structure):
        """
        Wrapper for:
            typedef struct vorbis_dsp_state vorbis_dsp_state;
        """
        _fields_ = [("analysisp", c_int),
                    ("vi", POINTER(vorbis_info)),
                    ("pcm", c_float_p_p),
                    ("pcmret", c_float_p_p),
                    ("pcm_storage", c_int),
                    ("pcm_current", c_int),
                    ("pcm_returned", c_int),

                    ("preextrapolate", c_int),
                    ("eofflag", c_int),

                    ("lW", c_long),
                    ("W", c_long),
                    ("nW", c_long),
                    ("centerW", c_long),

                    ("granulepos", ogg_int64_t),
                    ("sequence", ogg_int64_t),

                    ("glue_bits", ogg_int64_t),
                    ("time_bits", ogg_int64_t),
                    ("floor_bits", ogg_int64_t),
                    ("res_bits", ogg_int64_t),

                    ("backend_state", c_void_p)]
        
    class alloc_chain(ctypes.Structure):
        """
        Wrapper for:
            typedef struct alloc_chain;
        """
        pass

    alloc_chain._fields_ = [("ptr", c_void_p),
                    ("next", POINTER(alloc_chain))]

    class vorbis_block(ctypes.Structure):
        """
        Wrapper for:
            typedef struct vorbis_block vorbis_block;
        """
        _fields_ = [("pcm", c_float_p_p),
                    ("opb", oggpack_buffer),
                    ("lW", c_long),
                    ("W", c_long),
                    ("nW", c_long),
                    ("pcmend", c_int),
                    ("mode", c_int),

                    ("eofflag", c_int),
                    ("granulepos", ogg_int64_t),
                    ("sequence", ogg_int64_t),
                    ("vd", POINTER(vorbis_dsp_state)),

                    ("localstore", c_void_p),
                    ("localtop", c_long),
                    ("localalloc", c_long),
                    ("totaluse", c_long),
                    ("reap", POINTER(alloc_chain)),

                    ("glue_bits", c_long),
                    ("time_bits", c_long),
                    ("floor_bits", c_long),
                    ("res_bits", c_long),

                    ("internal", c_void_p)]

    class vorbis_comment(ctypes.Structure):
        """
        Wrapper for:
            typedef struct vorbis_comment vorbis_comment;
        """
        _fields_ = [("user_comments", c_char_p_p),
                    ("comment_lengths", c_int_p),
                    ("comments", c_int),
                    ("vendor", c_char_p)]

        

    vi_p = POINTER(vorbis_info)
    vc_p = POINTER(vorbis_comment)
    vd_p = POINTER(vorbis_dsp_state)
    vb_p = POINTER(vorbis_block)

    libvorbis.vorbis_info_init.restype = None
    libvorbis.vorbis_info_init.argtypes = [vi_p]
    def vorbis_info_init(vi):
        libvorbis.vorbis_info_init(vi)

    libvorbis.vorbis_info_clear.restype = None
    libvorbis.vorbis_info_clear.argtypes = [vi_p]
    def vorbis_info_clear(vi):
        libvorbis.vorbis_info_clear(vi)

    libvorbis.vorbis_info_blocksize.restype = c_int
    libvorbis.vorbis_info_blocksize.argtypes = [vi_p, c_int]
    def vorbis_info_blocksize(vi, zo):
        return libvorbis.vorbis_info_blocksize(vi, zo)

    libvorbis.vorbis_comment_init.restype = None
    libvorbis.vorbis_comment_init.argtypes = [vc_p]
    def vorbis_comment_init(vc):
        libvorbis.vorbis_comment_init(vc)

    libvorbis.vorbis_comment_add.restype = None
    libvorbis.vorbis_comment_add.argtypes = [vc_p, c_char_p]
    def vorbis_comment_add(vc, comment):
        libvorbis.vorbis_comment_add(vc, comment)

    libvorbis.vorbis_comment_add_tag.restype = None
    libvorbis.vorbis_comment_add_tag.argtypes = [vc_p, c_char_p, c_char_p]
    def vorbis_comment_add_tag(vc, tag, comment):
        libvorbis.vorbis_comment_add_tag(vc, tag, comment)

    libvorbis.vorbis_comment_query.restype = c_char_p
    libvorbis.vorbis_comment_query.argtypes = [vc_p, c_char_p, c_int]
    def vorbis_comment_query(vc, tag, count):
        libvorbis.vorbis_comment_query(vc, tag, count)

    libvorbis.vorbis_comment_query_count.restype = c_int
    libvorbis.vorbis_comment_query_count.argtypes = [vc_p, c_char_p]
    def vorbis_comment_query_count(vc, tag):
        libvorbis.vorbis_comment_query_count(vc, tag)

    libvorbis.vorbis_comment_clear.restype = None
    libvorbis.vorbis_comment_clear.argtypes = [vc_p]
    def vorbis_comment_clear(vc):
        libvorbis.vorbis_comment_clear(vc)


        
    libvorbis.vorbis_block_init.restype = c_int
    libvorbis.vorbis_block_init.argtypes = [vd_p, vb_p]
    def vorbis_block_init(v,vb):
        return libvorbis.vorbis_block_init(v,vb)

    libvorbis.vorbis_block_clear.restype = c_int
    libvorbis.vorbis_block_clear.argtypes = [vb_p]
    def vorbis_block_clear(vb):
        return libvorbis.vorbis_block_clear(vb)

    libvorbis.vorbis_dsp_clear.restype = None
    libvorbis.vorbis_dsp_clear.argtypes = [vd_p]
    def vorbis_dsp_clear(v):
        return libvorbis.vorbis_dsp_clear(v)

    libvorbis.vorbis_granule_time.restype = c_double
    libvorbis.vorbis_granule_time.argtypes = [vd_p, ogg_int64_t]
    def vorbis_granule_time(v, granulepos):
        return libvorbis.vorbis_granule_time(v, granulepos)


        
    libvorbis.vorbis_version_string.restype = c_char_p
    libvorbis.vorbis_version_string.argtypes = []
    def vorbis_version_string():
        return libvorbis.vorbis_version_string()





    libvorbis.vorbis_analysis_init.restype = c_int
    libvorbis.vorbis_analysis_init.argtypes = [vd_p, vi_p]
    def vorbis_analysis_init(v, vi):
        return libvorbis.vorbis_analysis_init(v, vi)

    libvorbis.vorbis_commentheader_out.restype = c_int
    libvorbis.vorbis_commentheader_out.argtypes = [vc_p, op_p]
    def vorbis_commentheader_out(vc, op):
        return libvorbis.vorbis_commentheader_out(vc, op)
        
    libvorbis.vorbis_analysis_headerout.restype = c_int
    libvorbis.vorbis_analysis_headerout.argtypes = [vd_p, vc_p, op_p, op_p, op_p]
    def vorbis_analysis_headerout(v,vc, op, op_comm, op_code):
        return libvorbis.vorbis_analysis_headerout(v,vc, op, op_comm, op_code)

    libvorbis.vorbis_analysis_buffer.restype = c_float_p_p
    libvorbis.vorbis_analysis_buffer.argtypes = [vd_p, c_int]
    def vorbis_analysis_buffer(v, vals):
        return libvorbis.vorbis_analysis_buffer(v, vals)

    libvorbis.vorbis_analysis_wrote.restype = c_int
    libvorbis.vorbis_analysis_wrote.argtypes = [vd_p, c_int]
    def vorbis_analysis_wrote(v, vals):
        return libvorbis.vorbis_analysis_wrote(v, vals)

    libvorbis.vorbis_analysis_blockout.restype = c_int
    libvorbis.vorbis_analysis_blockout.argtypes = [vd_p, vb_p]
    def vorbis_analysis_blockout(v, vb):
        return libvorbis.vorbis_analysis_blockout(v, vb)
        
    libvorbis.vorbis_analysis.restype = c_int
    libvorbis.vorbis_analysis.argtypes = [vb_p, op_p]
    def vorbis_analysis(vb, op):
        return libvorbis.vorbis_analysis(vb, op)




    libvorbis.vorbis_bitrate_addblock.restype = c_int
    libvorbis.vorbis_bitrate_addblock.argtypes = [vb_p]
    def vorbis_bitrate_addblock(vb):
        return libvorbis.vorbis_bitrate_addblock(vb)
        
    libvorbis.vorbis_bitrate_flushpacket.restype = c_int
    libvorbis.vorbis_bitrate_flushpacket.argtypes = [vd_p, op_p]
    def vorbis_bitrate_flushpacket(vd, op):
        return libvorbis.vorbis_bitrate_flushpacket(vd, op)




    libvorbis.vorbis_synthesis_idheader.restype = c_int
    libvorbis.vorbis_synthesis_idheader.argtypes = [op_p]
    def vorbis_synthesis_idheader(op):
        return libvorbis.vorbis_synthesis_idheader(op)
        
    libvorbis.vorbis_synthesis_headerin.restype = c_int
    libvorbis.vorbis_synthesis_headerin.argtypes = [vi_p, vc_p, op_p]
    def vorbis_synthesis_headerin(vi, vc, op):
        return libvorbis.vorbis_synthesis_headerin(vi, vc, op)




    libvorbis.vorbis_synthesis_init.restype = c_int
    libvorbis.vorbis_synthesis_init.argtypes = [vd_p, vi_p]
    def vorbis_synthesis_init(v,vi):
        return libvorbis.vorbis_synthesis_init(v,vi)

    libvorbis.vorbis_synthesis_restart.restype = c_int
    libvorbis.vorbis_synthesis_restart.argtypes = [vd_p]
    def vorbis_synthesis_restart(v):
        return libvorbis.vorbis_synthesis_restart(v)

    libvorbis.vorbis_synthesis.restype = c_int
    libvorbis.vorbis_synthesis.argtypes = [vb_p, op_p]
    def vorbis_synthesis(vb, op):
        return libvorbis.vorbis_synthesis(vb, op)

    libvorbis.vorbis_synthesis_trackonly.restype = c_int
    libvorbis.vorbis_synthesis_trackonly.argtypes = [vb_p, op_p]
    def vorbis_synthesis_trackonly(vb, op):
        return libvorbis.vorbis_synthesis_trackonly(vb, op)
        
    libvorbis.vorbis_synthesis_blockin.restype = c_int
    libvorbis.vorbis_synthesis_blockin.argtypes = [vd_p, vb_p]
    def vorbis_synthesis_blockin(v, vb):
        return libvorbis.vorbis_synthesis_blockin(v, vb)

    libvorbis.vorbis_synthesis_pcmout.restype = c_int
    libvorbis.vorbis_synthesis_pcmout.argtypes = [vd_p, c_float_p_p_p]
    def vorbis_synthesis_pcmout(v, pcm):
        return libvorbis.vorbis_synthesis_pcmout(v, pcm)
        
    libvorbis.vorbis_synthesis_lapout.restype = c_int
    libvorbis.vorbis_synthesis_lapout.argtypes = [vd_p, c_float_p_p_p]
    def vorbis_synthesis_lapout(v, pcm):
        return libvorbis.vorbis_synthesis_lapout(v, pcm)

    libvorbis.vorbis_synthesis_read.restype = c_int
    libvorbis.vorbis_synthesis_read.argtypes = [vd_p, c_int]
    def vorbis_synthesis_read(v, samples):
        return libvorbis.vorbis_synthesis_read(v, samples)
        
    libvorbis.vorbis_packet_blocksize.restype = c_long
    libvorbis.vorbis_packet_blocksize.argtypes = [vi_p, op_p]
    def vorbis_packet_blocksize(vi, op):
        return libvorbis.vorbis_packet_blocksize(vi, op)



    libvorbis.vorbis_synthesis_halfrate.restype = c_int
    libvorbis.vorbis_synthesis_halfrate.argtypes = [vi_p, c_int]
    def vorbis_synthesis_halfrate(v, flag):
        return libvorbis.vorbis_synthesis_halfrate(v, flag)
        
    libvorbis.vorbis_synthesis_halfrate_p.restype = c_int
    libvorbis.vorbis_synthesis_halfrate_p.argtypes = [vi_p]
    def vorbis_synthesis_halfrate_p(vi):
        return libvorbis.vorbis_synthesis_halfrate_p(vi)

    OV_FALSE =     -1
    OV_EOF  =      -2
    OV_HOLE  =     -3

    OV_EREAD  =    -128
    OV_EFAULT    = -129
    OV_EIMPL      =-130
    OV_EINVAL     =-131
    OV_ENOTVORBIS =-132
    OV_EBADHEADER =-133
    OV_EVERSION   =-134
    OV_ENOTAUDIO  =-135
    OV_EBADPACKET =-136
    OV_EBADLINK   =-137
    OV_ENOSEEK    =-138
    # end of codecs

    # vorbisfile
    read_func = ctypes.CFUNCTYPE(c_size_t,
                                 c_void_p,
                                 c_size_t,
                                 c_size_t,
                                 c_void_p)

    seek_func = ctypes.CFUNCTYPE(c_int,
                                 c_void_p,
                                 ogg_int64_t,
                                 c_int)

    close_func = ctypes.CFUNCTYPE(c_int,
                                  c_void_p)

    tell_func = ctypes.CFUNCTYPE(c_long,
                                 c_void_p)

    class ov_callbacks(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ov_callbacks;
        """

        _fields_ = [("read_func", read_func),
                    ("seek_func", seek_func),
                    ("close_func", close_func),
                    ("tell_func", tell_func)]
        
    NOTOPEN   = 0
    PARTOPEN  = 1
    OPENED    = 2
    STREAMSET = 3
    INITSET   = 4

    class OggVorbis_File(ctypes.Structure):
        """
        Wrapper for:
            typedef struct OggVorbis_File OggVorbis_File;
        """

        _fields_ = [("datasource", c_void_p),
                    ("seekable", c_int),
                    ("offset", ogg_int64_t),
                    ("end", ogg_int64_t),
                    ("oy", ogg_sync_state),

                    ("links", c_int),
                    ("offsets", ogg_int64_t_p),
                    ("dataoffsets", ogg_int64_t_p),
                    ("serialnos", c_long_p),
                    ("pcmlengths", ogg_int64_t_p),
                    ("vi", vi_p),
                    ("vc", vc_p),

                    ("pcm_offset", ogg_int64_t),
                    ("ready_state", c_int),
                    ("current_serialno", c_long),
                    ("current_link", c_int),

                    ("bittrack", c_double),
                    ("samptrack", c_double),

                    ("os", ogg_stream_state),

                    ("vd", vorbis_dsp_state),
                    ("vb", vorbis_block),

                    ("callbacks", ov_callbacks)]
    vf_p = POINTER(OggVorbis_File)

    libvorbisfile.ov_clear.restype = c_int
    libvorbisfile.ov_clear.argtypes = [vf_p]

    def ov_clear(vf):
        return libvorbisfile.ov_clear(vf)

    libvorbisfile.ov_fopen.restype = c_int
    libvorbisfile.ov_fopen.argtypes = [c_char_p, vf_p]

    def ov_fopen(path, vf):
        return libvorbisfile.ov_fopen(to_char_p(path), vf)

    libvorbisfile.ov_open_callbacks.restype = c_int
    libvorbisfile.ov_open_callbacks.argtypes = [c_void_p, vf_p, c_char_p, c_long, ov_callbacks]

    def ov_open_callbacks(datasource, vf, initial, ibytes, callbacks):
        return libvorbisfile.ov_open_callbacks(datasource, vf, initial, ibytes, callbacks)

    def ov_open(*args, **kw):
        raise PyOggError("ov_open is not supported, please use ov_fopen instead")

    def ov_test(*args, **kw):
        raise PyOggError("ov_test is not supported")

    libvorbisfile.ov_test_callbacks.restype = c_int
    libvorbisfile.ov_test_callbacks.argtypes = [c_void_p, vf_p, c_char_p, c_long, ov_callbacks]

    def ov_test_callbacks(datasource, vf, initial, ibytes, callbacks):
        return libvorbisfile.ov_test_callbacks(datasource, vf, initial, ibytes, callbacks)

    libvorbisfile.ov_test_open.restype = c_int
    libvorbisfile.ov_test_open.argtypes = [vf_p]

    def ov_test_open(vf):
        return libvorbisfile.ov_test_open(vf)




    libvorbisfile.ov_bitrate.restype = c_long
    libvorbisfile.ov_bitrate.argtypes = [vf_p, c_int]

    def ov_bitrate(vf, i):
        return libvorbisfile.ov_bitrate(vf, i)

    libvorbisfile.ov_bitrate_instant.restype = c_long
    libvorbisfile.ov_bitrate_instant.argtypes = [vf_p]

    def ov_bitrate_instant(vf):
        return libvorbisfile.ov_bitrate_instant(vf)

    libvorbisfile.ov_streams.restype = c_long
    libvorbisfile.ov_streams.argtypes = [vf_p]

    def ov_streams(vf):
        return libvorbisfile.ov_streams(vf)

    libvorbisfile.ov_seekable.restype = c_long
    libvorbisfile.ov_seekable.argtypes = [vf_p]

    def ov_seekable(vf):
        return libvorbisfile.ov_seekable(vf)

    libvorbisfile.ov_serialnumber.restype = c_long
    libvorbisfile.ov_serialnumber.argtypes = [vf_p, c_int]

    def ov_serialnumber(vf, i):
        return libvorbisfile.ov_serialnumber(vf, i)



    libvorbisfile.ov_raw_total.restype = ogg_int64_t
    libvorbisfile.ov_raw_total.argtypes = [vf_p, c_int]

    def ov_raw_total(vf, i):
        return libvorbisfile.ov_raw_total(vf, i)

    libvorbisfile.ov_pcm_total.restype = ogg_int64_t
    libvorbisfile.ov_pcm_total.argtypes = [vf_p, c_int]

    def ov_pcm_total(vf, i):
        return libvorbisfile.ov_pcm_total(vf, i)

    libvorbisfile.ov_time_total.restype = c_double
    libvorbisfile.ov_time_total.argtypes = [vf_p, c_int]

    def ov_time_total(vf, i):
        return libvorbisfile.ov_time_total(vf, i)




    libvorbisfile.ov_raw_seek.restype = c_int
    libvorbisfile.ov_raw_seek.argtypes = [vf_p, ogg_int64_t]

    def ov_raw_seek(vf, pos):
        return libvorbisfile.ov_raw_seek(vf, pos)

    libvorbisfile.ov_pcm_seek.restype = c_int
    libvorbisfile.ov_pcm_seek.argtypes = [vf_p, ogg_int64_t]

    def ov_pcm_seek(vf, pos):
        return libvorbisfile.ov_pcm_seek(vf, pos)

    libvorbisfile.ov_pcm_seek_page.restype = c_int
    libvorbisfile.ov_pcm_seek_page.argtypes = [vf_p, ogg_int64_t]

    def ov_pcm_seek_page(vf, pos):
        return libvorbisfile.ov_pcm_seek_page(vf, pos)

    libvorbisfile.ov_time_seek.restype = c_int
    libvorbisfile.ov_time_seek.argtypes = [vf_p, c_double]

    def ov_time_seek(vf, pos):
        return libvorbisfile.ov_time_seek(vf, pos)

    libvorbisfile.ov_time_seek_page.restype = c_int
    libvorbisfile.ov_time_seek_page.argtypes = [vf_p, c_double]

    def ov_time_seek_page(vf, pos):
        return libvorbisfile.ov_time_seek_page(vf, pos)




    libvorbisfile.ov_raw_seek_lap.restype = c_int
    libvorbisfile.ov_raw_seek_lap.argtypes = [vf_p, ogg_int64_t]

    def ov_raw_seek_lap(vf, pos):
        return libvorbisfile.ov_raw_seek_lap(vf, pos)

    libvorbisfile.ov_pcm_seek_lap.restype = c_int
    libvorbisfile.ov_pcm_seek_lap.argtypes = [vf_p, ogg_int64_t]

    def ov_pcm_seek_lap(vf, pos):
        return libvorbisfile.ov_pcm_seek_lap(vf, pos)

    libvorbisfile.ov_pcm_seek_page_lap.restype = c_int
    libvorbisfile.ov_pcm_seek_page_lap.argtypes = [vf_p, ogg_int64_t]

    def ov_pcm_seek_page_lap(vf, pos):
        return libvorbisfile.ov_pcm_seek_page_lap(vf, pos)

    libvorbisfile.ov_time_seek_lap.restype = c_int
    libvorbisfile.ov_time_seek_lap.argtypes = [vf_p, c_double]

    def ov_time_seek_lap(vf, pos):
        return libvorbisfile.ov_time_seek_lap(vf, pos)

    libvorbisfile.ov_time_seek_page_lap.restype = c_int
    libvorbisfile.ov_time_seek_page_lap.argtypes = [vf_p, c_double]

    def ov_time_seek_page_lap(vf, pos):
        return libvorbisfile.ov_time_seek_page_lap(vf, pos)



    libvorbisfile.ov_raw_tell.restype = ogg_int64_t
    libvorbisfile.ov_raw_tell.argtypes = [vf_p]

    def ov_raw_tell(vf):
        return libvorbisfile.ov_raw_tell(vf)

    libvorbisfile.ov_pcm_tell.restype = ogg_int64_t
    libvorbisfile.ov_pcm_tell.argtypes = [vf_p]

    def ov_pcm_tell(vf):
        return libvorbisfile.ov_pcm_tell(vf)

    libvorbisfile.ov_time_tell.restype = c_double
    libvorbisfile.ov_time_tell.argtypes = [vf_p]

    def ov_time_tell(vf):
        return libvorbisfile.ov_time_tell(vf)



    libvorbisfile.ov_info.restype = vi_p
    libvorbisfile.ov_info.argtypes = [vf_p, c_int]

    def ov_info(vf, link):
        return libvorbisfile.ov_info(vf, link)

    libvorbisfile.ov_comment.restype = vc_p
    libvorbisfile.ov_comment.argtypes = [vf_p, c_int]

    def ov_comment(vf, link):
        return libvorbisfile.ov_comment(vf, link)



    libvorbisfile.ov_read_float.restype = c_long
    libvorbisfile.ov_read_float.argtypes = [vf_p, c_float_p_p_p, c_int, c_int_p]

    def ov_read_float(vf, pcm_channels, samples, bitstream):
        return libvorbisfile.ov_read_float(vf, pcm_channels, samples, bitstream)

    filter_ = ctypes.CFUNCTYPE(None,
                              c_float_p_p,
                              c_long,
                              c_long,
                              c_void_p)

    try:
        libvorbisfile.ov_read_filter.restype = c_long
        libvorbisfile.ov_read_filter.argtypes = [vf_p, c_char_p, c_int, c_int, c_int, c_int, c_int_p, filter_, c_void_p]

        def ov_read_filter(vf, buffer, length, bigendianp, word, sgned, bitstream, filter_, filter_param):
            return libvorbisfile.ov_read_filter(vf, buffer, length, bigendianp, word, sgned, bitstream, filter_, filter_param)
    except:
        pass

    libvorbisfile.ov_read.restype = c_long
    libvorbisfile.ov_read.argtypes = [vf_p, c_char_p, c_int, c_int, c_int, c_int, c_int_p]

    def ov_read(vf, buffer, length, bigendianp, word, sgned, bitstream):
        return libvorbisfile.ov_read(vf, buffer, length, bigendianp, word, sgned, bitstream)

    libvorbisfile.ov_crosslap.restype = c_int
    libvorbisfile.ov_crosslap.argtypes = [vf_p, vf_p]

    def ov_crosslap(vf1, cf2):
        return libvorbisfile.ov_crosslap(vf1, vf2)




    libvorbisfile.ov_halfrate.restype = c_int
    libvorbisfile.ov_halfrate.argtypes = [vf_p, c_int]

    def ov_halfrate(vf, flag):
        return libvorbisfile.ov_halfrate(vf, flag)

    libvorbisfile.ov_halfrate_p.restype = c_int
    libvorbisfile.ov_halfrate_p.argtypes = [vf_p]

    def ov_halfrate_p(vf):
        return libvorbisfile.ov_halfrate_p(vf)
    # end of vorbisfile

    try:
        # vorbisenc
        
        # Sanity check also satisfies mypy type checking
        assert libvorbisenc is not None
        
        libvorbisenc.vorbis_encode_init.restype = c_int
        libvorbisenc.vorbis_encode_init.argtypes = [vi_p, c_long, c_long, c_long, c_long, c_long]

        def vorbis_encode_init(vi, channels, rate, max_bitrate, nominal_bitrate, min_bitrate):
            return libvorbisenc.vorbis_encode_init(vi, channels, rate, max_bitrate, nominal_bitrate, min_bitrate)

        libvorbisenc.vorbis_encode_setup_managed.restype = c_int
        libvorbisenc.vorbis_encode_setup_managed.argtypes = [vi_p, c_long, c_long, c_long, c_long, c_long]

        def vorbis_encode_setup_managed(vi, channels, rate, max_bitrate, nominal_bitrate, min_bitrate):
            return libvorbisenc.vorbis_encode_setup_managed(vi, channels, rate, max_bitrate, nominal_bitrate, min_bitrate)

        libvorbisenc.vorbis_encode_setup_vbr.restype = c_int
        libvorbisenc.vorbis_encode_setup_vbr.argtypes = [vi_p, c_long, c_long, c_float]

        def vorbis_encode_setup_vbr(vi, channels, rate, quality):
            return libvorbisenc.vorbis_encode_setup_vbr(vi, channels, rate, quality)

        libvorbisenc.vorbis_encode_init_vbr.restype = c_int
        libvorbisenc.vorbis_encode_init_vbr.argtypes = [vi_p, c_long, c_long, c_float]

        def vorbis_encode_init_vbr(vi, channels, rate, quality):
            return libvorbisenc.vorbis_encode_init_vbr(vi, channels, rate, quality)

        libvorbisenc.vorbis_encode_setup_init.restype = c_int
        libvorbisenc.vorbis_encode_setup_init.argtypes = [vi_p]

        def vorbis_encode_setup_init(vi):
            return libvorbisenc.vorbis_encode_setup_init(vi)

        libvorbisenc.vorbis_encode_ctl.restype = c_int
        libvorbisenc.vorbis_encode_ctl.argtypes = [vi_p, c_int, c_void_p]

        def vorbis_encode_ctl(vi, number, arg):
            return libvorbisenc.vorbis_encode_ctl(vi, number, arg)

        class ovectl_ratemanage_arg(ctypes.Structure):
            _fields_ = [("management_active", c_int),
                        ("bitrate_hard_min", c_long),
                        ("bitrate_hard_max", c_long),
                        ("bitrate_hard_window", c_double),
                        ("bitrate_av_lo", c_long),
                        ("bitrate_av_hi", c_long),
                        ("bitrate_av_window", c_double),
                        ("bitrate_av_window_center", c_double)]

        class ovectl_ratemanage2_arg(ctypes.Structure):
            _fields_ = [("management_active", c_int),
                        ("bitrate_limit_min_kbps", c_long),
                        ("bitrate_limit_max_kbps", c_long),
                        ("bitrate_limit_reservoir_bits", c_long),
                        ("bitrate_limit_reservoir_bias", c_double),
                        ("bitrate_average_kbps", c_long),
                        ("bitrate_average_damping", c_double)]

        OV_ECTL_RATEMANAGE2_GET      =0x14

        OV_ECTL_RATEMANAGE2_SET      =0x15

        OV_ECTL_LOWPASS_GET          =0x20

        OV_ECTL_LOWPASS_SET          =0x21

        OV_ECTL_IBLOCK_GET           =0x30

        OV_ECTL_IBLOCK_SET           =0x31

        OV_ECTL_COUPLING_GET         =0x40

        OV_ECTL_COUPLING_SET         =0x41

        OV_ECTL_RATEMANAGE_GET       =0x10

        OV_ECTL_RATEMANAGE_SET       =0x11

        OV_ECTL_RATEMANAGE_AVG       =0x12

        OV_ECTL_RATEMANAGE_HARD      =0x13
        # end of vorbisenc
    except:
        pass
