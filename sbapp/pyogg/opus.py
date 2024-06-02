############################################################
# Opus license:                                            #
############################################################
"""
Copyright 2001-2011 Xiph.Org, Skype Limited, Octasic,
                    Jean-Marc Valin, Timothy B. Terriberry,
                    CSIRO, Gregory Maxwell, Mark Borgerding,
                    Erik de Castro Lopo

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of Internet Society, IETF or IETF Trust, nor the
names of specific contributors, may be used to endorse or promote
products derived from this software without specific prior written
permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Opus is subject to the royalty-free patent licenses which are
specified at:

Xiph.Org Foundation:
https://datatracker.ietf.org/ipr/1524/

Microsoft Corporation:
https://datatracker.ietf.org/ipr/1914/

Broadcom Corporation:
https://datatracker.ietf.org/ipr/1526/
"""

############################################################
# Opusfile license:                                        #
############################################################
"""
Copyright (c) 1994-2013 Xiph.Org Foundation and contributors

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of the Xiph.Org Foundation nor the names of its
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

############################################################
# OpenSSL license:                                         #
############################################################
"""
/*
 * Copyright (c) 1998-2019 The OpenSSL Project.  All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. All advertising materials mentioning features or use of this
 *    software must display the following acknowledgment:
 *    "This product includes software developed by the OpenSSL Project
 *    for use in the OpenSSL Toolkit. (http://www.openssl.org/)"
 *
 * 4. The names "OpenSSL Toolkit" and "OpenSSL Project" must not be used to
 *    endorse or promote products derived from this software without
 *    prior written permission. For written permission, please contact
 *    openssl-core@openssl.org.
 *
 * 5. Products derived from this software may not be called "OpenSSL"
 *    nor may "OpenSSL" appear in their names without prior written
 *    permission of the OpenSSL Project.
 *
 * 6. Redistributions of any form whatsoever must retain the following
 *    acknowledgment:
 *    "This product includes software developed by the OpenSSL Project
 *    for use in the OpenSSL Toolkit (http://www.openssl.org/)"
 *
 * THIS SOFTWARE IS PROVIDED BY THE OpenSSL PROJECT ``AS IS'' AND ANY
 * EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE OpenSSL PROJECT OR
 * ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 * ====================================================================
 *
 * This product includes cryptographic software written by Eric Young
 * (eay@cryptsoft.com).  This product includes software written by Tim
 * Hudson (tjh@cryptsoft.com).
 *
 */
"""
############################################################
# Opusenc license:                                         #
############################################################
"""
Copyright (c) 1994-2013 Xiph.Org Foundation and contributors
Copyright (c) 2017 Jean-Marc Valin

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of the Xiph.Org Foundation nor the names of its
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
import os

from traceback import print_exc as _print_exc

from .ogg import *

from .library_loader import Library, ExternalLibrary, ExternalLibraryError

__here = os.getcwd()
libopus = None

try:
    names = {
        "Windows": "opus.dll",
        "Darwin": "libopus.0.dylib",
        "external": "opus"
    }
    libopus = Library.load(names, tests = [lambda lib: hasattr(lib, "opus_encoder_get_size")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

libopusfile = None

try:
    names = {
        "Windows": "opusfile.dll",
        "Darwin": "libopusfile.0.dylib",
        "external": "opusfile"
    }
    libopusfile = Library.load(names, tests = [lambda lib: hasattr(lib, "opus_head_parse")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

libopusenc = None

try:
    names = {
        "Windows": "opusenc.dll",
        "Darwin": "libopusenc.0.dylib",
        "external": "opusenc"
    }
    libopusenc = Library.load(names, tests = [lambda lib: hasattr(lib, "ope_comments_create")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

if libopus:
    PYOGG_OPUS_AVAIL = True
else:
    PYOGG_OPUS_AVAIL = False
    
if libopusfile:
    PYOGG_OPUS_FILE_AVAIL = True
else:
    PYOGG_OPUS_FILE_AVAIL = False

if libopusenc:
    PYOGG_OPUS_ENC_AVAIL = True
else:
    PYOGG_OPUS_ENC_AVAIL = False

# Definitions of C constants

# 2021-02-16: Moved definitions outside of test for PYOGG_OPUS_AVAIL
# and PYOGG_OPUS_FILE_AVAIL as the definitons don't actually require
# the libraries.

OPE_API_VERSION =0

OPE_OK =0
OPE_BAD_ARG =-11
OPE_INTERNAL_ERROR =-13
OPE_UNIMPLEMENTED =-15
OPE_ALLOC_FAIL =-17

OPE_CANNOT_OPEN =-30
OPE_TOO_LATE =-31
OPE_UNRECOVERABLE =-32
OPE_INVALID_PICTURE =-33
OPE_INVALID_ICON =-34

OPUS_OK                =0
OPUS_BAD_ARG          =-1
OPUS_BUFFER_TOO_SMALL =-2
OPUS_INTERNAL_ERROR   =-3
OPUS_INVALID_PACKET   =-4
OPUS_UNIMPLEMENTED    =-5
OPUS_INVALID_STATE    =-6
OPUS_ALLOC_FAIL       =-7

OP_FALSE         =(-1)
OP_EOF           =(-2)
OP_HOLE          =(-3)
OP_EREAD         =(-128)
OP_EFAULT        =(-129)
OP_EIMPL         =(-130)
OP_EINVAL        =(-131)
OP_ENOTFORMAT    =(-132)
OP_EBADHEADER    =(-133)
OP_EVERSION      =(-134)
OP_ENOTAUDIO     =(-135)
OP_EBADPACKET    =(-136)
OP_EBADLINK      =(-137)
OP_ENOSEEK       =(-138)
OP_EBADTIMESTAMP =(-139)

OP_PIC_FORMAT_UNKNOWN =(-1)
OP_PIC_FORMAT_URL     =(0)
OP_PIC_FORMAT_JPEG    =(1)
OP_PIC_FORMAT_PNG     =(2)
OP_PIC_FORMAT_GIF     =(3)


OPUS_CHANNEL_COUNT_MAX =(255)

OPUS_SET_APPLICATION_REQUEST         =4000
OPUS_GET_APPLICATION_REQUEST         =4001
OPUS_SET_BITRATE_REQUEST             =4002
OPUS_GET_BITRATE_REQUEST             =4003
OPUS_SET_MAX_BANDWIDTH_REQUEST       =4004
OPUS_GET_MAX_BANDWIDTH_REQUEST       =4005
OPUS_SET_VBR_REQUEST                 =4006
OPUS_GET_VBR_REQUEST                 =4007
OPUS_SET_BANDWIDTH_REQUEST           =4008
OPUS_GET_BANDWIDTH_REQUEST           =4009
OPUS_SET_COMPLEXITY_REQUEST          =4010
OPUS_GET_COMPLEXITY_REQUEST          =4011
OPUS_SET_INBAND_FEC_REQUEST          =4012
OPUS_GET_INBAND_FEC_REQUEST          =4013
OPUS_SET_PACKET_LOSS_PERC_REQUEST    =4014
OPUS_GET_PACKET_LOSS_PERC_REQUEST    =4015
OPUS_SET_DTX_REQUEST                 =4016
OPUS_GET_DTX_REQUEST                 =4017
OPUS_SET_VBR_CONSTRAINT_REQUEST      =4020
OPUS_GET_VBR_CONSTRAINT_REQUEST      =4021
OPUS_SET_FORCE_CHANNELS_REQUEST      =4022
OPUS_GET_FORCE_CHANNELS_REQUEST      =4023
OPUS_SET_SIGNAL_REQUEST              =4024
OPUS_GET_SIGNAL_REQUEST              =4025
OPUS_GET_LOOKAHEAD_REQUEST           =4027
OPUS_GET_SAMPLE_RATE_REQUEST         =4029
OPUS_GET_FINAL_RANGE_REQUEST         =4031
OPUS_GET_PITCH_REQUEST               =4033
OPUS_SET_GAIN_REQUEST                =4034
OPUS_GET_GAIN_REQUEST                =4045
OPUS_SET_LSB_DEPTH_REQUEST           =4036
OPUS_GET_LSB_DEPTH_REQUEST           =4037
OPUS_GET_LAoe_pACKET_DURATION_REQUEST =4039
OPUS_SET_EXPERT_FRAME_DURATION_REQUEST =4040
OPUS_GET_EXPERT_FRAME_DURATION_REQUEST =4041
OPUS_SET_PREDICTION_DISABLED_REQUEST =4042
OPUS_GET_PREDICTION_DISABLED_REQUEST =4043
OPUS_SET_PHASE_INVERSION_DISABLED_REQUEST =4046
OPUS_GET_PHASE_INVERSION_DISABLED_REQUEST =4047

OPUS_AUTO                           =-1000
OPUS_BITRATE_MAX                     =  -1

OPUS_APPLICATION_VOIP               = 2048
OPUS_APPLICATION_AUDIO              = 2049
OPUS_APPLICATION_RESTRICTED_LOWDELAY =2051

OPUS_SIGNAL_VOICE                    =3001
OPUS_SIGNAL_MUSIC                    =3002 
OPUS_BANDWIDTH_NARROWBAND            =1101 
OPUS_BANDWIDTH_MEDIUMBAND            =1102 
OPUS_BANDWIDTH_WIDEBAND              =1103 
OPUS_BANDWIDTH_SUPERWIDEBAND         =1104 
OPUS_BANDWIDTH_FULLBAND              =1105 

OPUS_FRAMESIZE_ARG                   =5000 
OPUS_FRAMESIZE_2_5_MS                =5001 
OPUS_FRAMESIZE_5_MS                  =5002 
OPUS_FRAMESIZE_10_MS                 =5003
OPUS_FRAMESIZE_20_MS                 =5004 
OPUS_FRAMESIZE_40_MS                 =5005 
OPUS_FRAMESIZE_60_MS                 =5006 
OPUS_FRAMESIZE_80_MS                 =5007 
OPUS_FRAMESIZE_100_MS                =5008 
OPUS_FRAMESIZE_120_MS                =5009

OPUS_MULTISTREAM_GET_ENCODER_STATE_REQUEST =5120
OPUS_MULTISTREAM_GET_DECODER_STATE_REQUEST =5122

OP_SSL_SKIP_CERTIFICATE_CHECK_REQUEST =(6464)
OP_HTTP_PROXY_HOST_REQUEST            =(6528)
OP_HTTP_PROXY_PORT_REQUEST            =(6592)
OP_HTTP_PROXY_USER_REQUEST            =(6656)
OP_HTTP_PROXY_PASS_REQUEST            =(6720)
OP_GET_SERVER_INFO_REQUEST            =(6784)

OP_DEC_FORMAT_SHORT =(7008)
OP_DEC_FORMAT_FLOAT =(7040)
OP_DEC_USE_DEFAULT  =(6720)

OP_HEADER_GAIN   =(0)
OP_ALBUM_GAIN    =(3007)
OP_TRACK_GAIN    =(3008)
OP_ABSOLUTE_GAIN =(3009)

OPUS_RESET_STATE =4028

OPE_SET_DECISION_DELAY_REQUEST      =14000
OPE_GET_DECISION_DELAY_REQUEST      =14001
OPE_SET_MUXING_DELAY_REQUEST        =14002
OPE_GET_MUXING_DELAY_REQUEST        =14003
OPE_SET_COMMENT_PADDING_REQUEST     =14004
OPE_GET_COMMENT_PADDING_REQUEST     =14005
OPE_SET_SERIALNO_REQUEST            =14006
OPE_GET_SERIALNO_REQUEST            =14007
OPE_SET_PACKET_CALLBACK_REQUEST     =14008
OPE_SET_HEADER_GAIN_REQUEST         =14010
OPE_GET_HEADER_GAIN_REQUEST         =14011

# opus_types

opus_int16 = c_int16
opus_int16_p = POINTER(c_int16)
opus_uint16 = c_uint16
opus_int32 = c_int32
opus_int32_p = POINTER(opus_int32)
opus_uint32 = c_uint32

opus_int  =  c_int  
opus_int64=  c_longlong
opus_int8=    c_int8

opus_uint= c_uint
opus_uint64 = c_ulonglong
opus_uint8 = c_int8

# /opus_types


if PYOGG_OPUS_AVAIL:
    # Sanity check also satisfies mypy type checking
    assert libopus is not None

    # opus

    class OpusEncoder(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_int)]

    oe_p = POINTER(OpusEncoder)

    libopus.opus_encoder_get_size.restype = c_int
    libopus.opus_encoder_get_size.argtypes = [c_int]

    def opus_encoder_get_size(channels):
        return libopus.opus_encoder_get_size(channels)

    libopus.opus_encoder_create.restype = oe_p
    libopus.opus_encoder_create.argtypes = [opus_int32, c_int, c_int, c_int_p]

    def opus_encoder_create(Fs, channels, application, error):
        return libopus.opus_encoder_create(Fs, channels, application, error)

    libopus.opus_encoder_init.restype = c_int
    libopus.opus_encoder_init.argtypes = [oe_p, opus_int32, c_int, c_int]

    def opus_encoder_init(st, Fs, channels, applications):
        return libopus.opus_encoder_init(st, Fs, channels, applications)

    libopus.opus_encode.restype = opus_int32
    libopus.opus_encode.argtypes = [oe_p, opus_int16_p, c_int, c_uchar_p, opus_int32]

    def opus_encode(st, pcm, frame_size, data, max_data_bytes):
        return libopus.opus_encode(st, pcm, frame_size, data, max_data_bytes)

    libopus.opus_encode_float.restype = opus_int32
    libopus.opus_encode_float.argtypes = [oe_p, c_float_p, c_int, c_uchar_p, opus_int32]

    def opus_encode_float(st, pcm, frame_size, data, max_data_bytes):
        return libopus.opus_encode_float(st, pcm, frame_size, data, max_data_bytes)

    libopus.opus_encoder_destroy.restype = None
    libopus.opus_encoder_destroy.argtypes = [oe_p]

    def opus_encoder_destroy(st):
        return libopus.opus_encoder_destroy(st)

    libopus.opus_encoder_ctl.restype = c_int
    libopus.opus_encoder_ctl.argtypes = [oe_p, c_int]

    def opus_encoder_ctl(st, request, *args):
        return libopus.opus_encoder_ctl(st, request, *args)

    class OpusDecoder(ctypes.Structure):
        _fields_ = [("dummy", c_int)]

    od_p = POINTER(OpusDecoder)

    libopus.opus_decoder_get_size.restype = c_int
    libopus.opus_decoder_get_size.argtypes = [c_int]

    def opus_decoder_get_size(channels):
        return libopus.opus_decoder_get_size(channels)

    libopus.opus_decoder_create.restype = od_p
    libopus.opus_decoder_create.argtypes = [opus_int32, c_int, c_int_p]

    def opus_decoder_create(Fs, channels, error):
        return libopus.opus_decoder_create(Fs, channels, error)

    libopus.opus_decoder_init.restype = c_int
    libopus.opus_decoder_init.argtypes = [od_p, opus_int32, c_int]

    def opus_decoder_init(st, Fs, channels):
        return libopus.opus_decoder_init(st, Fs, channels)

    libopus.opus_decode.restype = c_int
    libopus.opus_decode.argtypes = [od_p, c_uchar_p, opus_int32, opus_int16_p, c_int, c_int]

    def opus_decode(st, data, len, pcm, frame_size, decode_fec):
        return libopus.opus_decode(st, data, len, pcm, frame_size, decode_fec)

    libopus.opus_decode_float.restype = c_int
    libopus.opus_decode_float.argtypes = [od_p, c_uchar_p, opus_int32, c_float_p, c_int, c_int]

    def opus_decode_float(st, data, len, pcm, frame_size, decode_fec):
        return libopus.opus_decode_float(st, data, len, pcm, frame_size, decode_fec)

    libopus.opus_decoder_ctl.restype = c_int
    libopus.opus_decoder_ctl.argtypes = [od_p, c_int]

    def opus_decoder_ctl(st, request, *args):
        return libopus.opus_decoder_ctl(st, request, *args)

    libopus.opus_decoder_destroy.restype = None
    libopus.opus_decoder_destroy.argtypes = [od_p]

    def opus_decoder_destroy(st):
        return libopus.opus_decoder_destroy(st)

    libopus.opus_packet_parse.restype = c_int
    libopus.opus_packet_parse.argtypes = [c_uchar_p, opus_int32, c_uchar_p, c_uchar_p*48, opus_int16*48, c_int_p]

    def opus_packet_parse(data, len, out_toc, frames, size, payload_offset):
        return libopus.opus_packet_parse(data, len, out_toc, frames, size, payload_offset)

    libopus.opus_packet_get_bandwidth.restype = c_int
    libopus.opus_packet_get_bandwidth.argtypes = [c_uchar_p]

    def opus_packet_get_bandwidth(data):
        return libopus.opus_packet_get_bandwidth(data)

    libopus.opus_packet_get_samples_per_frame.restype = c_int
    libopus.opus_packet_get_samples_per_frame.argtypes = [c_uchar_p, opus_int32]

    def opus_packet_get_samples_per_frame(data, Fs):
        return libopus.opus_packet_get_samples_per_frame(data, Fs)

    libopus.opus_packet_get_nb_channels.restype = c_int
    libopus.opus_packet_get_nb_channels.argtypes = [c_uchar_p]

    def opus_packet_get_nb_channels(data):
        return libopus.opus_packet_get_nb_channels(data)

    libopus.opus_packet_get_nb_frames.restype = c_int
    libopus.opus_packet_get_nb_frames.argtypes = [c_uchar*0, opus_int32]

    def opus_packet_get_nb_frames(packet, len):
        return libopus.opus_packet_get_nb_frames(packet, len)

    libopus.opus_packet_get_nb_samples.restype = c_int
    libopus.opus_packet_get_nb_samples.argtypes = [c_uchar*0, opus_int32, opus_int32]

    def opus_packet_get_nb_samples(packet, len, Fs):
        return libopus.opus_packet_get_nb_samples(packet, len, Fs)

    libopus.opus_decoder_get_nb_samples.restype = c_int
    libopus.opus_decoder_get_nb_samples.argtypes = [od_p, c_uchar*0, opus_int32]

    def opus_decoder_get_nb_samples(dec, packet, len):
        return libopus.opus_decoder_get_nb_samples(dec, packet, len)

    libopus.opus_pcm_soft_clip.restype = None
    libopus.opus_pcm_soft_clip.argtypes = [c_float_p, c_int, c_int, c_float_p]

    def opus_pcm_soft_clip(pcm, frame_size, channels, softclip_mem):
        return libopus.opus_pcm_soft_clip(pcm, frame_size, channels, softclip_mem)

    class OpusRepacketizer(ctypes.Structure):
        _fields_ = [("dummy", c_int)]

    or_p = POINTER(OpusRepacketizer)

    libopus.opus_repacketizer_get_size.restype = c_int
    libopus.opus_repacketizer_get_size.argtypes = []

    def opus_repacketizer_get_size():
        return libopus.opus_repacketizer_get_size()

    libopus.opus_repacketizer_init.restype = or_p
    libopus.opus_repacketizer_init.argtypes = [or_p]

    def opus_repacketizer_init(rp):
        return libopus.opus_repacketizer_init(rp)

    libopus.opus_repacketizer_create.restype = or_p
    libopus.opus_repacketizer_create.argtypes = []

    def opus_repacketizer_create():
        return libopus.opus_repacketizer_create()

    libopus.opus_repacketizer_destroy.restype = None
    libopus.opus_repacketizer_destroy.argtypes = [or_p]

    def opus_repacketizer_destroy(rp):
        return libopus.opus_repacketizer_destroy(rp)

    libopus.opus_repacketizer_cat.restype = c_int
    libopus.opus_repacketizer_cat.argtypes = [or_p, c_uchar_p, opus_int32]

    def opus_repacketizer_cat(rp, data, len):
        return libopus.opus_repacketizer_cat(rp, data, len)

    libopus.opus_repacketizer_out_range.restype = opus_int32
    libopus.opus_repacketizer_out_range.argtypes = [or_p, c_int, c_int, c_uchar_p, opus_int32]

    def opus_repacketizer_out_range(rp, begin, end, data, maxlen):
        return libopus.opus_repacketizer_out_range(rp, begin, end, data, maxlen)

    libopus.opus_repacketizer_get_nb_frames.restype = c_int
    libopus.opus_repacketizer_get_nb_frames.argtypes = [or_p]

    def opus_repacketizer_get_nb_frames(rp):
        return libopus.opus_repacketizer_get_nb_frames(rp)

    libopus.opus_repacketizer_out.restype = opus_int32
    libopus.opus_repacketizer_out.argtypes = [or_p, c_uchar_p, opus_int32]

    def opus_repacketizer_out(rp, data, maxlen):
        return libopus.opus_repacketizer_out(rp, data, maxlen)

    libopus.opus_packet_pad.restype = c_int
    libopus.opus_packet_pad.argtypes = [c_uchar_p, opus_int32, opus_int32]

    def opus_packet_pad(data, len, new_len):
        return libopus.opus_packet_pad(data, len, new_len)

    libopus.opus_packet_unpad.restype = opus_int32
    libopus.opus_packet_unpad.argtypes = [c_uchar_p, opus_int32]

    def opus_packet_unpad(data, len):
        return libopus.opus_packet_unpad(data, len)

    libopus.opus_multistream_packet_pad.restype = c_int
    libopus.opus_multistream_packet_pad.argtypes = [c_uchar_p, opus_int32, opus_int32, c_int]

    def opus_multistream_packet_pad(data, len, new_len, nb_streams):
        return libopus.opus_multistream_packet_pad(data, len, new_len, nb_streams)

    libopus.opus_multistream_packet_unpad.restype = opus_int32
    libopus.opus_multistream_packet_unpad.argtypes = [c_uchar_p, opus_int32, c_int]

    def opus_multistream_packet_unpad(data, len, nb_streams):
        return libopus.opus_multistream_packet_unpad(data, len, nb_streams)
      
    libopus.opus_strerror.restype = c_char_p
    libopus.opus_strerror.argtypes = [c_int]

    def opus_strerror(error):
        return libopus.opus_strerror(error)

    libopus.opus_get_version_string.restype = c_char_p
    libopus.opus_get_version_string.argtypes = []

    def opus_get_version_string():
        return libopus.opus_get_version_string()

    # /opus

    # opus_multistream
    class OpusMSEncoder(ctypes.Structure):
        _fields_ = [("dummy", c_int)]
    omse_p = POINTER(OpusMSEncoder)

    class OpusMSDecoder(ctypes.Structure):
        _fields_ = [("dummy", c_int)]
    omsd_p = POINTER(OpusMSDecoder)

    libopus.opus_multistream_encoder_get_size.restype = opus_int32
    libopus.opus_multistream_encoder_get_size.argtypes = [c_int, c_int]

    def opus_multistream_encoder_get_size(streams, coupled_streams):
        return libopus.opus_multistream_encoder_get_size(streams, coupled_streams)

    libopus.opus_multistream_surround_encoder_get_size.restype = opus_int32
    libopus.opus_multistream_surround_encoder_get_size.argtypes = [c_int, c_int]

    def opus_multistream_surround_encoder_get_size(channels, mapping_family):
        return libopus.opus_multistream_surround_encoder_get_size(channels, mapping_family)

    libopus.opus_multistream_encoder_create.restype = omse_p
    libopus.opus_multistream_encoder_create.argtypes = [opus_int32, c_int, c_int, c_int, c_uchar_p, c_int, c_int_p]

    def opus_multistream_encoder_create(Fs, channels,streams,coupled_streams, mapping, application, error):
        return libopus.opus_multistream_encoder_create(Fs, channels,streams,coupled_streams, mapping, application, error)

    libopus.opus_multistream_surround_encoder_create.restype = omse_p
    libopus.opus_multistream_surround_encoder_create.argtypes = [opus_int32, c_int, c_int, c_int_p, c_int_p, c_uchar_p, c_int, c_int_p]

    def opus_multistream_surround_encoder_create(Fs, channels, mapping_family, streams, coupled_streams, mapping, application, error):
        return libopus.opus_multistream_surround_encoder_create(Fs, channels, mapping_family, streams, coupled_streams, mapping, application, error)

    libopus.opus_multistream_encoder_init.restype = c_int
    libopus.opus_multistream_encoder_init.argtypes = [omse_p, opus_int32, c_int, c_int, c_int, c_uchar_p, c_int]

    def opus_multistream_encoder_init(st, Fs, channels, streams, coupled_streams, mapping, application):
        return libopus.opus_multistream_encoder_init(st, Fs, channels, streams, coupled_streams, mapping, application)

    libopus.opus_multistream_surround_encoder_init.restype = c_int
    libopus.opus_multistream_surround_encoder_init.argtypes = [omse_p, opus_int32, c_int, c_int, c_int_p, c_int_p, c_uchar_p, c_int]

    def opus_multistream_surround_encoder_init(st, Fs, channels, mapping_family, streams, coupled_streams, mapping, application):
        return libopus.opus_multistream_surround_encoder_init(st, Fs, channels, mapping_family, streams, coupled_streams, mapping, application)

    libopus.opus_multistream_encode.restype = c_int
    libopus.opus_multistream_encode.argtypes = [omse_p, opus_int16_p, c_int, c_uchar_p, opus_int32]

    def opus_multistream_encode(st, pcm, frame_size, data, max_data_bytes):
        return libopus.opus_multistream_encode(st, pcm, frame_size, data, max_data_bytes)

    libopus.opus_multistream_encode_float.restype = c_int
    libopus.opus_multistream_encode_float.argtypes = [omse_p, c_float_p, c_int, c_uchar_p, opus_int32]

    def opus_multistream_encode_float(st, pcm, frame_size, data, max_data_bytes):
        return libopus.opus_multistream_encode_float(st, pcm, frame_size, data, max_data_bytes)

    libopus.opus_multistream_encoder_destroy.restype = None
    libopus.opus_multistream_encoder_destroy.argtypes = [omse_p]

    def opus_multistream_encoder_destroy(st):
        return libopus.opus_multistream_encoder_destroy(st)

    libopus.opus_multistream_encoder_ctl.restype = c_int
    libopus.opus_multistream_encoder_ctl.argtypes = [omse_p, c_int]

    def opus_multistream_encoder_ctl(st, request, *args):
        return libopus.opus_multistream_encoder_ctl(st, request, *args)

    libopus.opus_multistream_decoder_get_size.restype = opus_int32
    libopus.opus_multistream_decoder_get_size.argtypes = [c_int, c_int]

    def opus_multistream_decoder_get_size(streams, coupled_streams):
        return libopus.opus_multistream_decoder_get_size(streams, coupled_streams)

    libopus.opus_multistream_decoder_create.restype = omsd_p
    libopus.opus_multistream_decoder_create.argtypes = [opus_int32, c_int, c_int, c_int, c_uchar_p, c_int_p]

    def opus_multistream_decoder_create(Fs, channels, streams, coupled_streams, mapping, error):
        return libopus.opus_multistream_decoder_create(Fs, channels, streams, coupled_streams, mapping, error)

    libopus.opus_multistream_decoder_init.restype = c_int
    libopus.opus_multistream_decoder_init.argtypes = [omsd_p, opus_int32, c_int, c_int, c_int, c_uchar_p]

    def opus_multistream_decoder_init(st, Fs, channels, streams, coupled_streams, mapping):
        return libopus.opus_multistream_decoder_init(st, Fs, channels, streams, coupled_streams, mapping)

    libopus.opus_multistream_decode.restype = c_int
    libopus.opus_multistream_decode.argtypes = [omsd_p, c_uchar_p, opus_int32, opus_int16_p, c_int, c_int]

    def opus_multistream_decode(st, data, len, pcm, frame_size, decode_fec):
        return libopus.opus_multistream_decode(st, data, len, pcm, frame_size, decode_fec)

    libopus.opus_multistream_decode_float.restype = c_int
    libopus.opus_multistream_decode_float.argtypes = [omsd_p, c_uchar_p, opus_int32, c_float_p, c_int, c_int]

    def opus_multistream_decode_float(st, data, len, pcm, frame_size, decode_fec):
        return libopus.opus_multistream_decode_float(st, data, len, pcm, frame_size, decode_fec)

    libopus.opus_multistream_decoder_ctl.restype = c_int
    libopus.opus_multistream_decoder_ctl.argtypes = [omsd_p, c_int]

    def opus_multistream_decoder_ctl(st, request, *args):
        return libopus.opus_multistream_decoder_ctl(st, request, *args)

    libopus.opus_multistream_decoder_destroy.restype = None
    libopus.opus_multistream_decoder_destroy.argtypes = [omsd_p]

    def opus_multistream_decoder_destroy(st):
        return libopus.opus_multistream_decoder_destroy(st)

    # /opus_multistream

    if PYOGG_OPUS_FILE_AVAIL:
        assert libopusfile is not None
    
        # opusfile

        class OggOpusFile(ctypes.Structure):
            _fields_ = [("dummy", c_int)]

        oof_p = POINTER(OggOpusFile)



        class OpusHead(ctypes.Structure):
            _fields_ = [("version", c_int),
                        ("channel_count", c_int),
                        ("pre_skip", c_uint),
                        ("input_sample_rate", opus_uint32),
                        ("output_gain", c_int),
                        ("mapping_family", c_int),
                        ("stream_count", c_int),
                        ("coupled_count", c_int),
                        ("mapping", c_uchar * OPUS_CHANNEL_COUNT_MAX)]

        oh_p = POINTER(OpusHead)

        class OpusTags(ctypes.Structure):
            _fields_ = [("user_comments", c_char_p_p),
                        ("comment_lengths", c_int_p),
                        ("comments", c_int),
                        ("vendor", c_char_p)]

        ot_p = POINTER(OpusTags)



        class OpusPictureTag(ctypes.Structure):
            _fields_ = [("type", opus_int32),
                        ("mime_type", c_char_p),
                        ("description", c_char_p),
                        ("width", opus_uint32),
                        ("height", opus_uint32),
                        ("depth", opus_uint32),
                        ("colors", opus_uint32),
                        ("data_length", opus_uint32),
                        ("data", c_uchar_p),
                        ("format", c_int)]

        opt_p = POINTER(OpusPictureTag)

        libopusfile.opus_head_parse.restype = c_int
        libopusfile.opus_head_parse.argtypes = [oh_p, c_uchar_p, c_size_t]

        def opus_head_parse(_head, _data, _len):
            return libopusfile.opus_head_parse(_head, _data, _len)

        libopusfile.opus_granule_sample.restype = ogg_int64_t
        libopusfile.opus_granule_sample.argtypes = [oh_p, ogg_int64_t]

        def opus_granule_sample(_head, _gp):
            return libopusfile.opus_granule_sample(_head, _gp)

        libopusfile.opus_tags_parse.restype = c_int
        libopusfile.opus_tags_parse.argtypes = [ot_p, c_uchar_p, c_size_t]

        def opus_tags_parse(_tags, _data, _len):
            return libopusfile.opus_tags_parse(_tags, _data, _len)

        libopusfile.opus_tags_copy.restype = c_int
        libopusfile.opus_tags_copy.argtypes = [ot_p, ot_p]

        def opus_tags_copy(_dst, _src):
            return libopusfile.opus_tags_copy(_dst, _src)

        libopusfile.opus_tags_init.restype = None
        libopusfile.opus_tags_init.argtypes = [ot_p]

        def opus_tags_init(_tags):
            return libopusfile.opus_tags_init(_tags)

        libopusfile.opus_tags_add.restype = c_int
        libopusfile.opus_tags_add.argtypes = [ot_p, c_char_p, c_char_p]

        def opus_tags_add(_tags, _tag, _value):
            return libopusfile.opus_tags_add(_tags, _tag, _value)

        libopusfile.opus_tags_add_comment.restype = c_int
        libopusfile.opus_tags_add_comment.argtypes = [ot_p, c_char_p]

        def opus_tags_add_comment(_tags, _comment):
            return libopusfile.opus_tags_add_comment(_tags, _comment)

        libopusfile.opus_tags_set_binary_suffix.restype = c_int
        libopusfile.opus_tags_set_binary_suffix.argtypes = [ot_p, c_uchar_p, c_int]

        def opus_tags_set_binary_suffix(_tags, _data, _len):
            return libopusfile.opus_tags_set_binary_suffix(_tags, _data, _len)

        libopusfile.opus_tags_query.restype = c_char_p
        libopusfile.opus_tags_query.argtypes = [ot_p, c_char_p, c_int]

        def opus_tags_query(_tags, _tag, _count):
            return libopusfile.opus_tags_query(_tags, _tag, _count)

        libopusfile.opus_tags_query_count.restype = c_int
        libopusfile.opus_tags_query_count.argtypes = [ot_p, c_char_p]

        def opus_tags_query_count(_tags, _tag):
            return libopusfile.opus_tags_query_count(_tags, _tag)

        libopusfile.opus_tags_get_binary_suffix.restype = c_uchar_p
        libopusfile.opus_tags_get_binary_suffix.argtypes = [ot_p, c_int_p]

        def opus_tags_get_binary_suffix(_tags, _len):
            return libopusfile.opus_tags_get_binary_suffix(_tags, _len)

        libopusfile.opus_tags_get_album_gain.restype = c_int
        libopusfile.opus_tags_get_album_gain.argtypes = [ot_p, c_int_p]

        def opus_tags_get_album_gain(_tags, _gain_q8):
            return libopusfile.opus_tags_get_album_gain(_tags, _gain_q8)

        libopusfile.opus_tags_get_track_gain.restype = c_int
        libopusfile.opus_tags_get_track_gain.argtypes = [ot_p, c_int_p]

        def opus_tags_get_track_gain(_tags, _gain_q8):
            return libopusfile.opus_tags_get_track_gain(_tags, _gain_q8)

        libopusfile.opus_tags_clear.restype = None
        libopusfile.opus_tags_clear.argtypes = [ot_p]

        def opus_tags_clear(_tags):
            return libopusfile.opus_tags_clear(_tags)

        libopusfile.opus_tagcompare.restype = c_int
        libopusfile.opus_tagcompare.argtypes = [c_char_p, c_char_p]

        def opus_tagcompare(_tag_name, _comment):
            return libopusfile.opus_tagcompare(_tag_name, _comment)

        libopusfile.opus_tagncompare.restype = c_int
        libopusfile.opus_tagncompare.argtypes = [c_char_p, c_int, c_char_p]

        def opus_tagncompare(_tag_name, _tag_len, _comment):
            return libopusfile.opus_tagncompare(_tag_name, _tag_len, _comment)

        libopusfile.opus_picture_tag_parse.restype = c_int
        libopusfile.opus_picture_tag_parse.argtypes = [opt_p, c_char_p]

        def opus_picture_tag_parse(_pic, _tag):
            return libopusfile.opus_picture_tag_parse(_pic, _tag)

        libopusfile.opus_picture_tag_init.restype = None
        libopusfile.opus_picture_tag_init.argtypes = [opt_p]

        def opus_picture_tag_init(_pic):
            return libopusfile.opus_picture_tag_init(_pic)

        libopusfile.opus_picture_tag_clear.restype = None
        libopusfile.opus_picture_tag_clear.argtypes = [opt_p]

        def opus_picture_tag_clear(_pic):
            return libopusfile.opus_picture_tag_clear(_pic)



        class OpusServerInfo(ctypes.Structure):
            _fields_ = [("name", c_char_p),
                        ("description", c_char_p),
                        ("genre", c_char_p),
                        ("url", c_char_p),
                        ("server", c_char_p),
                        ("content_type", c_char_p),
                        ("bitrate_kbps", opus_int32),
                        ("is_public", c_int),
                        ("is_ssl", c_int)]

        osi_p = POINTER(OpusServerInfo)
        try:
            libopusfile.opus_server_info_init.restype = None
            libopusfile.opus_server_info_init.argtypes = [osi_p]

            def opus_server_info_init(_info):
                return libopusfile.opus_server_info_init(_info)

            libopusfile.opus_server_info_clear.restype = None
            libopusfile.opus_server_info_clear.argtypes = [osi_p]

            def opus_server_info_clear(_info):
                return libopusfile.opus_server_info_clear(_info)
        except:
            pass

        op_read_func = ctypes.CFUNCTYPE(c_int,
                                        c_void_p,
                                        c_uchar_p,
                                        c_int)

        op_seek_func = ctypes.CFUNCTYPE(c_int,
                                        c_void_p,
                                        opus_int64,
                                        c_int)

        op_tell_func = ctypes.CFUNCTYPE(opus_int64,
                                        c_void_p)

        op_close_func = ctypes.CFUNCTYPE(c_int,
                                        c_void_p)

        class OpusFileCallbacks(ctypes.Structure):
            _fields_ = [("read", op_read_func),
                        ("seek", op_seek_func),
                        ("tell", op_tell_func),
                        ("close", op_close_func)]

        ofc_p = POINTER(OpusFileCallbacks)

        libopusfile.op_fopen.restype = c_void_p
        libopusfile.op_fopen.argtypes = [ofc_p, c_char_p, c_char_p]

        def op_fopen(_cb, _path, _mode):
            return libopusfile.op_fopen(_cb, _path, _mode)

        libopusfile.op_fdopen.restype = c_void_p
        libopusfile.op_fdopen.argtypes = [ofc_p, c_int, c_char_p]

        def op_fdopen(_cb, _fd, _mode):
            return libopusfile.op_fdopen(_cb, _fd, _mode)

        libopusfile.op_freopen.restype = c_void_p
        libopusfile.op_freopen.argtypes = [ofc_p, c_char_p, c_char_p, c_void_p]

        def op_freopen(_cb, _path, _mode, _stream):
            return libopusfile.op_freopen(_cb, _path, _mode, _stream)

        libopusfile.op_mem_stream_create.restype = c_void_p
        libopusfile.op_mem_stream_create.argtypes = [ofc_p, c_uchar_p, c_size_t]

        def op_mem_stream_create(_cb, _data, _size):
            return libopusfile.op_mem_stream_create(_cb, _data, _size)

        libopusfile.op_test.restype = c_int
        libopusfile.op_test.argtypes = [oh_p, c_uchar_p, c_size_t]

        def op_test(_head, _initial_data, _initial_bytes):
            return libopusfile.op_test(_head, _initial_data, _initial_bytes)

        libopusfile.op_open_file.restype = oof_p
        libopusfile.op_open_file.argtypes = [c_char_p, c_int_p]

        def op_open_file(_path, _error):
            return libopusfile.op_open_file(_path, _error)

        libopusfile.op_open_memory.restype = oof_p
        libopusfile.op_open_memory.argtypes = [c_uchar_p, c_size_t, c_int_p]

        def op_open_memory(_data, _size, _error):
            return libopusfile.op_open_memory(_data, _size, _error)

        libopusfile.op_open_callbacks.restype = oof_p
        libopusfile.op_open_callbacks.argtypes = [c_void_p, ofc_p, c_uchar_p, c_size_t, c_int_p]

        def op_open_callbacks(_source, _cb, _initial_data, _initial_bytes, _error):
            return libopusfile.op_open_callbacks(_source, _cb, _initial_data, _initial_bytes, _error)

        libopusfile.op_test_file.restype = oof_p
        libopusfile.op_test_file.argtypes = [c_char_p, c_int_p]

        def op_test_file(_path, _error):
            return libopusfile.op_test_file(_path, _error)

        libopusfile.op_test_memory.restype = oof_p
        libopusfile.op_test_memory.argtypes = [c_uchar_p, c_size_t, c_int_p]

        def op_test_memory(_data, _size, _error):
            return libopusfile.op_test_memory(_data, _size, _error)

        libopusfile.op_test_callbacks.restype = oof_p
        libopusfile.op_test_callbacks.argtypes = [c_void_p, ofc_p, c_uchar_p, c_size_t, c_int_p]

        def op_test_callbacks(_source, _cb, _initial_data, _initial_bytes, _error):
            return libopusfile.op_test_callbacks(_source, _cb, _initial_data, _initial_bytes, _error)

        libopusfile.op_test_open.restype = c_int
        libopusfile.op_test_open.argtypes = [oof_p]

        def op_test_open(_of):
            return libopusfile.op_test_open(_of)

        libopusfile.op_free.restype = None
        libopusfile.op_free.argtypes = [oof_p]

        def op_free(_of):
            return libopusfile.op_free(_of)

        libopusfile.op_seekable.restype = c_int
        libopusfile.op_seekable.argtypes = [oof_p]

        def op_seekable(_of):
            return libopusfile.op_seekable(_of)

        libopusfile.op_link_count.restype = c_int
        libopusfile.op_link_count.argtypes = [oof_p]

        def op_link_count(_of):
            return libopusfile.op_link_count(_of)

        libopusfile.op_serialno.restype = opus_uint32
        libopusfile.op_serialno.argtypes = [oof_p, c_int]

        def op_serialno(_of, _li):
            return libopusfile.op_serialno(_of, _li)

        libopusfile.op_channel_count.restype = c_int
        libopusfile.op_channel_count.argtypes = [oof_p, c_int]

        def op_channel_count(_of, _li):
            return libopusfile.op_channel_count(_of, _li)

        libopusfile.op_raw_total.restype = opus_int64
        libopusfile.op_raw_total.argtypes = [oof_p, c_int]

        def op_raw_total(_of, _li):
            return libopusfile.op_raw_total(_of, _li)

        libopusfile.op_pcm_total.restype = ogg_int64_t
        libopusfile.op_pcm_total.argtypes = [oof_p, c_int]

        def op_pcm_total(_of, _li):
            return libopusfile.op_pcm_total(_of, _li)

        libopusfile.op_head.restype = oh_p
        libopusfile.op_head.argtypes = [oof_p, c_int]

        def op_head(_of, _li):
            return libopusfile.op_head(_of, _li)

        libopusfile.op_tags.restype = ot_p
        libopusfile.op_tags.argtypes = [oof_p, c_int]

        def op_tags(_of, _li):
            return libopusfile.op_tags(_of, _li)

        libopusfile.op_current_link.restype = c_int
        libopusfile.op_current_link.argtypes = [oof_p]

        def op_current_link(_of):
            return libopusfile.op_current_link(_of)

        libopusfile.op_bitrate.restype = opus_int32
        libopusfile.op_bitrate.argtypes = [oof_p, c_int]

        def op_bitrate(_of, _li):
            return libopusfile.op_bitrate(_of, _li)

        libopusfile.op_bitrate_instant.restype = opus_int32
        libopusfile.op_bitrate_instant.argtypes = [oof_p]

        def op_bitrate_instant(_of):
            return libopusfile.op_bitrate_instant(_of)

        libopusfile.op_raw_tell.restype = opus_int64
        libopusfile.op_raw_tell.argtypes = [oof_p]

        def op_raw_tell(_of):
            return libopusfile.op_raw_tell(_of)

        libopusfile.op_pcm_tell.restype = ogg_int64_t
        libopusfile.op_pcm_tell.argtypes = [oof_p]

        def op_pcm_tell(_of):
            return libopusfile.op_pcm_tell(_of)

        libopusfile.op_raw_seek.restype = c_int
        libopusfile.op_raw_seek.argtypes = [oof_p, opus_int64]

        def op_raw_seek(_of, _byte_offset):
            return libopusfile.op_raw_seek(_of, _byte_offset)

        libopusfile.op_pcm_seek.restype = c_int
        libopusfile.op_pcm_seek.argtypes = [oof_p,ogg_int64_t]

        def op_pcm_seek(_of, _pcm_offset):
            return libopusfile.op_pcm_seek(_of, _pcm_offset)



        op_decode_cb_func = ctypes.CFUNCTYPE(c_int,
                                             c_void_p,
                                             omsd_p,
                                             c_void_p,
                                             op_p,
                                             c_int,
                                             c_int,
                                             c_int,
                                             c_int)

        libopusfile.op_set_decode_callback.restype = None
        libopusfile.op_set_decode_callback.argtypes = [oof_p, op_decode_cb_func, c_void_p]

        def op_set_decode_callback(_of, _decode_cb, _ctx):
            return libopusfile.op_set_decode_callback(_of, _decode_cb, _ctx)



        libopusfile.op_set_gain_offset.restype = c_int
        libopusfile.op_set_gain_offset.argtypes = [oof_p, c_int, opus_int32]

        def op_set_gain_offset(_of, _gain_type, _gain_offset_q8):
            return libopusfile.op_set_gain_offset(_of, _gain_type, _gain_offset_q8)

        libopusfile.op_set_dither_enabled.restype = None
        libopusfile.op_set_dither_enabled.argtypes = [oof_p, c_int]

        def op_set_dither_enabled(_of, _enabled):
            return libopusfile.op_set_dither_enabled(_of, _enabled)

        libopusfile.op_read.restype = c_int
        libopusfile.op_read.argtypes = [oof_p, opus_int16_p, c_int, c_int_p]

        def op_read(_of, _pcm, _buf_size, _li):
            return libopusfile.op_read(_of, _pcm, _buf_size, _li)

        libopusfile.op_read_float.restype = c_int
        libopusfile.op_read_float.argtypes = [oof_p, c_float_p, c_int, c_int_p]

        def op_read_float(_of, _pcm, _buf_size, _li):
            return libopusfile.op_read_float(_of, _pcm, _buf_size, _li)

        libopusfile.op_read_stereo.restype = c_int
        libopusfile.op_read_stereo.argtypes = [oof_p, opus_int16_p, c_int]

        def op_read_stereo(_of, _pcm, _buf_size):
            return libopusfile.op_read_stereo(_of, _pcm, _buf_size)

        libopusfile.op_read_float_stereo.restype = c_int
        libopusfile.op_read_float_stereo.argtypes = [oof_p, c_float_p, c_int]

        def op_read_float_stereo(_of, _pcm, _buf_size):
            return libopusfile.op_read_float_stereo(_of, _pcm, _buf_size)


    if PYOGG_OPUS_ENC_AVAIL:
        # Sanity check also satisfies mypy type checking
        assert libopusenc is not None
        
        ope_write_func = ctypes.CFUNCTYPE(c_int,
                                          c_void_p,
                                          c_uchar_p,
                                          opus_int32)

        ope_close_func = ctypes.CFUNCTYPE(c_int,
                                          c_void_p)

        ope_packet_func = ctypes.CFUNCTYPE(c_int,
                                          c_void_p,
                                          c_uchar_p,
                                          opus_int32,
                                          opus_uint32)


        class OpusEncCallbacks(ctypes.Structure):
            _fields_ = [("write", ope_write_func),
                        ("close", ope_close_func)]

        oec_p = POINTER(OpusEncCallbacks)

        class OggOpusComments(ctypes.Structure):
            _fields_ = [("dummy", c_int)]

        ooc_p = POINTER(OggOpusComments)

        class OggOpusEnc(ctypes.Structure):
            _fields_ = [("dummy", c_int)]

        ooe_p = POINTER(OggOpusEnc)

        libopusenc.ope_comments_create.restype = ooc_p
        libopusenc.ope_comments_create.argtypes = []

        def ope_comments_create():
            return libopusenc.ope_comments_create()

        libopusenc.ope_comments_copy.restype = ooc_p
        libopusenc.ope_comments_copy.argtypes = [ooc_p]

        def ope_comments_copy(comments):
            return libopusenc.ope_comments_copy(comments)

        libopusenc.ope_comments_destroy.restype = None
        libopusenc.ope_comments_destroy.argtypes = [ooc_p]

        def ope_comments_destroy(comments):
            return libopusenc.ope_comments_destroy(comments)

        libopusenc.ope_comments_add.restype = c_int
        libopusenc.ope_comments_add.argtypes = [ooc_p, c_char_p, c_char_p]

        def ope_comments_add(comments, tag, val):
            return libopusenc.ope_comments_add(comments, tag, val)

        libopusenc.ope_comments_add_string.restype = c_int
        libopusenc.ope_comments_add_string.argtypes = [ooc_p, c_char_p]

        def ope_comments_add_string(comments, tag_and_val):
            return libopusenc.ope_comments_add_string(comments, tag_and_val)

        libopusenc.ope_comments_add_picture.restype = c_int
        libopusenc.ope_comments_add_picture.argtypes = [ooc_p, c_char_p, c_int, c_char_p]

        def ope_comments_add_picture(comments, filename, picture_type, description):
            return libopusenc.ope_comments_add_picture(comments, filename, picture_type, description)

        libopusenc.ope_encoder_create_file.restype = ooe_p
        libopusenc.ope_encoder_create_file.argtypes = [c_char_p, ooc_p, opus_int32, c_int, c_int, c_int_p]

        def ope_encoder_create_file(path, comments, rate, channels, family, error):
            return libopusenc.ope_encoder_create_file(path, comments, rate, channels, family, error)

        libopusenc.ope_encoder_create_callbacks.restype = ooe_p
        libopusenc.ope_encoder_create_callbacks.argtypes = [oec_p, c_void_p, ooc_p, opus_int32, c_int, c_int, c_int_p]

        def ope_encoder_create_callbacks(callbacks, user_data, comments, rate, channels, family, error):
            return libopusenc.ope_encoder_create_callbacks(callbacks, user_data, comments, rate, channels, family, error)

        libopusenc.ope_encoder_create_pull.restype = ooe_p
        libopusenc.ope_encoder_create_pull.argtypes = [ooc_p, opus_int32, c_int, c_int, c_int_p]

        def ope_encoder_create_pull(comments, rate, channels, family, error):
            return libopusenc.ope_encoder_create_pull(comments, rate, channels, family, error)

        libopusenc.ope_encoder_write_float.restype = c_int
        libopusenc.ope_encoder_write_float.argtypes = [ooe_p, c_float_p, c_int]

        def ope_encoder_write_float(enc, pcm, samples_per_channel):
            return libopusenc.ope_encoder_write_float(enc, pcm, samples_per_channel)

        libopusenc.ope_encoder_write.restype = c_int
        libopusenc.ope_encoder_write.argtypes = [ooe_p, opus_int16_p, c_int]

        def ope_encoder_write(enc, pcm, samples_per_channel):
            return libopusenc.ope_encoder_write(enc, pcm, samples_per_channel)

        libopusenc.ope_encoder_get_page.restype = c_int
        libopusenc.ope_encoder_get_page.argtypes = [ooe_p, POINTER(c_uchar_p), opus_int32_p, c_int]

        def ope_encoder_get_page(enc, page, len, flush):
            return libopusenc.ope_encoder_get_page(enc, page, len, flush)

        libopusenc.ope_encoder_drain.restype = c_int
        libopusenc.ope_encoder_drain.argtypes = [ooe_p]

        def ope_encoder_drain(enc):
            return libopusenc.ope_encoder_drain(enc)

        libopusenc.ope_encoder_destroy.restype = None
        libopusenc.ope_encoder_destroy.argtypes = [ooe_p]

        def ope_encoder_destroy(enc):
            return libopusenc.ope_encoder_destroy(enc)

        libopusenc.ope_encoder_chain_current.restype = c_int
        libopusenc.ope_encoder_chain_current.argtypes = [ooe_p, ooc_p]

        def ope_encoder_chain_current(enc, comments):
            return libopusenc.ope_encoder_chain_current(enc, comments)

        libopusenc.ope_encoder_continue_new_file.restype = c_int
        libopusenc.ope_encoder_continue_new_file.argtypes = [ooe_p, c_char_p, ooc_p]

        def ope_encoder_continue_new_file(enc,path, comments):
            return libopusenc.ope_encoder_continue_new_file(enc,path, comments)

        libopusenc.ope_encoder_continue_new_callbacks.restype = c_int
        libopusenc.ope_encoder_continue_new_callbacks.argtypes = [ooe_p, c_void_p, ooc_p]

        def ope_encoder_continue_new_callbacks(enc,user_data, comments):
            return libopusenc.ope_encoder_continue_new_callbacks(enc,user_data, comments)

        libopusenc.ope_encoder_flush_header.restype = c_int
        libopusenc.ope_encoder_flush_header.argtypes = [ooe_p]

        def ope_encoder_flush_header(enc):
            return libopusenc.ope_encoder_flush_header(enc)

        libopusenc.ope_encoder_ctl.restype = c_int
        libopusenc.ope_encoder_ctl.argtypes = [ooe_p, c_int]

        def ope_encoder_ctl(enc, request, *args):
            return libopusenc.ope_encoder_ctl(enc, request, *args)

        libopusenc.ope_strerror.restype = c_char_p
        libopusenc.ope_strerror.argtypes = [c_int]

        def ope_strerror(error):
            return libopusenc.ope_strerror(error)

        libopusenc.ope_get_version_string.restype = c_char_p
        libopusenc.ope_get_version_string.argtypes = []

        def ope_get_version_string():
            return libopusenc.ope_get_version_string()

        libopusenc.ope_get_abi_version.restype = c_int
        libopusenc.ope_get_abi_version.argtypes = []

        def ope_get_abi_version():
            return libopusenc.ope_get_abi_version()
