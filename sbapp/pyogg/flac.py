############################################################
# Flac license:                                            #
############################################################
"""
Copyright (C) 2000-2009  Josh Coalson
Copyright (C) 2011-2016  Xiph.Org Foundation

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
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import ctypes
from ctypes import c_int, c_int8, c_int16, c_int32, c_int64, c_uint, c_uint8, c_uint16, c_uint32, c_uint64, c_float, c_long, c_ulong, c_char, c_bool, c_char_p, c_ubyte, c_longlong, c_ulonglong, c_size_t, c_void_p, c_double, POINTER, pointer, cast, CFUNCTYPE, Structure, Union
import ctypes.util
import sys
from traceback import print_exc as _print_exc
import os

from .ogg import *

from .library_loader import ExternalLibrary, ExternalLibraryError

__here = os.getcwd()

libflac = None

try:
    names = {
        "Windows": "libFLAC.dll",
        "Darwin": "libFLAC.8.dylib",
        "external": "FLAC"
    }
    libflac = Library.load(names, tests = [lambda lib: hasattr(lib, "FLAC__EntropyCodingMethodTypeString")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

if libflac:
    PYOGG_FLAC_AVAIL = True
else:
    PYOGG_FLAC_AVAIL = False
    
# ctypes
c_ubyte_p = POINTER(c_ubyte)
c_uchar_p = c_ubyte_p
c_uint_p = POINTER(c_uint)
c_size_t_p = POINTER(c_size_t)
c_off_t = c_int32
# /ctypes

if PYOGG_FLAC_AVAIL:
    # Sanity check also satisfies mypy type checking
    assert libflac is not None
    
    # ordinals

    FLAC__int8 = c_int8
    FLAC__uint8 = c_uint8

    FLAC__int16 = c_int16

    FLAC__int32 = c_int32
    FLAC__int32_p = POINTER(FLAC__int32)

    FLAC__int64 = c_int64
    FLAC__uint16 = c_uint16
    FLAC__uint32 = c_uint32
    FLAC__uint64 = c_uint64

    FLAC__uint64_p = POINTER(FLAC__uint64)

    FLAC__bool = c_bool

    FLAC__byte = c_uint8

    FLAC__byte_p = POINTER(FLAC__byte)

    c_char_p_p = POINTER(c_char_p)

    # /ordinals

    # callback

    FLAC__IOHandle = CFUNCTYPE(c_void_p)

    FLAC__IOCallback_Read = CFUNCTYPE(c_size_t,
                                      c_void_p,
                                      c_size_t,
                                      c_size_t,
                                      FLAC__IOHandle)

    FLAC__IOCallback_Write = CFUNCTYPE(c_size_t, c_void_p, c_size_t, c_size_t, FLAC__IOHandle)

    FLAC__IOCallback_Seek = CFUNCTYPE(c_int, FLAC__IOHandle, FLAC__int64, c_int)

    FLAC__IOCallback_Tell = CFUNCTYPE(FLAC__int64, FLAC__IOHandle)

    FLAC__IOCallback_Eof = CFUNCTYPE(c_int, FLAC__IOHandle)

    FLAC__IOCallback_Close = CFUNCTYPE(c_int, FLAC__IOHandle)

    class FLAC__IOCallbacks(Structure):
        _fields_ = [("read", FLAC__IOCallback_Read),
                    ("write", FLAC__IOCallback_Write),
                    ("seek", FLAC__IOCallback_Seek),
                    ("tell", FLAC__IOCallback_Tell),
                    ("eof", FLAC__IOCallback_Eof),
                    ("close", FLAC__IOCallback_Close)]

    # /callback

    # format

    FLAC__MAX_METADATA_TYPE_CODE =(126)
    FLAC__MIN_BLOCK_SIZE =(16)
    FLAC__MAX_BLOCK_SIZE =(65535)
    FLAC__SUBSET_MAX_BLOCK_SIZE_48000HZ =(4608)
    FLAC__MAX_CHANNELS =(8)
    FLAC__MIN_BITS_PER_SAMPLE =(4)
    FLAC__MAX_BITS_PER_SAMPLE =(32)
    FLAC__REFERENCE_CODEC_MAX_BITS_PER_SAMPLE =(24)
    FLAC__MAX_SAMPLE_RATE =(655350)
    FLAC__MAX_LPC_ORDER =(32)
    FLAC__SUBSET_MAX_LPC_ORDER_48000HZ =(12)
    FLAC__MIN_QLP_COEFF_PRECISION =(5)
    FLAC__MAX_QLP_COEFF_PRECISION =(15)
    FLAC__MAX_FIXED_ORDER =(4)
    FLAC__MAX_RICE_PARTITION_ORDER =(15)
    FLAC__SUBSET_MAX_RICE_PARTITION_ORDER =(8)

    FLAC__VERSION_STRING = c_char_p.in_dll(libflac, "FLAC__VERSION_STRING")

    FLAC__VENDOR_STRING = c_char_p.in_dll(libflac, "FLAC__VENDOR_STRING")

    FLAC__STREAM_SYNC_STRING = (FLAC__byte * 4).in_dll(libflac, "FLAC__STREAM_SYNC_STRING")

    FLAC__STREAM_SYNC = c_uint.in_dll(libflac, "FLAC__STREAM_SYNC")

    FLAC__STREAM_SYNC_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_SYNC_LEN")

    FLAC__STREAM_SYNC_LENGTH =(4)



    FLAC__EntropyCodingMethodType = c_int

    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE = 0
            
    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE2 = 1



    libflac.FLAC__EntropyCodingMethodTypeString.restype = c_char_p
    libflac.FLAC__EntropyCodingMethodTypeString.argtypes = []

    def FLAC__EntropyCodingMethodTypeString():
        return libflac.FLAC__EntropyCodingMethodTypeString()



    class FLAC__EntropyCodingMethod_PartitionedRiceContents(Structure):
        _fields_ = [("parameters", c_uint_p),
                    ("raw_bits", c_uint_p),
                    ("capacity_by_order", c_uint)]

    class FLAC__EntropyCodingMethod_PartitionedRice(Structure):
        _fields_ = [("order", c_uint),
                    ("contents", POINTER(FLAC__EntropyCodingMethod_PartitionedRiceContents))]


    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_ORDER_LEN = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_ORDER_LEN")

    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_PARAMETER_LEN = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_PARAMETER_LEN")

    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE2_PARAMETER_LEN = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE2_PARAMETER_LEN")

    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_RAW_LEN = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_RAW_LEN")

    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_ESCAPE_PARAMETER = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE_ESCAPE_PARAMETER")


    class FLAC__EntropyCodingMethod_data(Union):
        _fields_ = [("partitioned_rice", FLAC__EntropyCodingMethod_PartitionedRice)]

    class FLAC__EntropyCodingMethod(Structure):
        _fields_ = [("type", POINTER(FLAC__EntropyCodingMethodType)),
                    ("data", FLAC__EntropyCodingMethod_data)]

    FLAC__ENTROPY_CODING_METHOD_TYPE_LEN = c_uint.in_dll(libflac, "FLAC__ENTROPY_CODING_METHOD_TYPE_LEN")



    FLAC__SubframeType = c_int
    FLAC__SUBFRAME_TYPE_CONSTANT = 0
    FLAC__SUBFRAME_TYPE_VERBATIM = 1
    FLAC__SUBFRAME_TYPE_FIXED = 2
    FLAC__SUBFRAME_TYPE_LPC = 3



    libflac.FLAC__SubframeTypeString.restype = c_char_p
    libflac.FLAC__SubframeTypeString.argtypes = []

    def FLAC__SubframeTypeString():
        return libflac.FLAC__SubframeTypeString()



    class FLAC__Subframe_Constant(Structure):
        _fields_ = [("value", FLAC__int32)]


    class FLAC__Subframe_Verbatim(Structure):
        _fields_ = [("data", FLAC__int32_p)]


    class FLAC__Subframe_Fixed(Structure):
        _fields_ = [("entropy_coding_method", FLAC__EntropyCodingMethod),
                    ("order", c_uint),
                    ("warmup", FLAC__int32 * FLAC__MAX_FIXED_ORDER),
                    ("residual", FLAC__int32_p)]


    class FLAC__Subframe_LPC(Structure):
        _fields_ = [("entropy_coding_method", FLAC__EntropyCodingMethod),
                    ("order", c_uint),
                    ("qlp_coeff_precision", c_uint),
                    ("quantization_level", c_int),
                    ("qlp_coeff", FLAC__int32 * FLAC__MAX_LPC_ORDER),
                    ("warmup", FLAC__int32 * FLAC__MAX_LPC_ORDER),
                    ("residual", FLAC__int32_p)]


    FLAC__SUBFRAME_LPC_QLP_COEFF_PRECISION_LEN = c_uint.in_dll(libflac, "FLAC__SUBFRAME_LPC_QLP_COEFF_PRECISION_LEN")

    FLAC__SUBFRAME_LPC_QLP_SHIFT_LEN = c_uint.in_dll(libflac, "FLAC__SUBFRAME_LPC_QLP_SHIFT_LEN")



    class FLAC__Subframe_data(Union):
        _fields_ = [("constant", FLAC__Subframe_Constant),
                    ("fixed", FLAC__Subframe_Fixed),
                    ("lpc", FLAC__Subframe_LPC),
                    ("verbatim", FLAC__Subframe_Verbatim)]

    class FLAC__Subframe(Structure):
        _fields_ = [("type", FLAC__SubframeType),
                    ("data", FLAC__Subframe_data),
                    ("wasted_bits", c_uint)]
        

    FLAC__SUBFRAME_ZERO_PAD_LEN = c_uint.in_dll(libflac, "FLAC__SUBFRAME_ZERO_PAD_LEN")
    
    FLAC__SUBFRAME_TYPE_LEN = c_uint.in_dll(libflac, "FLAC__SUBFRAME_TYPE_LEN")

    FLAC__SUBFRAME_WASTED_BITS_FLAG_LEN = c_uint.in_dll(libflac, "FLAC__SUBFRAME_WASTED_BITS_FLAG_LEN")

    FLAC__SUBFRAME_TYPE_CONSTANT_BYTE_ALIGNED_MASK = c_uint.in_dll(libflac, "FLAC__SUBFRAME_TYPE_CONSTANT_BYTE_ALIGNED_MASK")

    FLAC__SUBFRAME_TYPE_VERBATIM_BYTE_ALIGNED_MASK = c_uint.in_dll(libflac, "FLAC__SUBFRAME_TYPE_VERBATIM_BYTE_ALIGNED_MASK")

    FLAC__SUBFRAME_TYPE_FIXED_BYTE_ALIGNED_MASK = c_uint.in_dll(libflac, "FLAC__SUBFRAME_TYPE_FIXED_BYTE_ALIGNED_MASK")

    FLAC__SUBFRAME_TYPE_LPC_BYTE_ALIGNED_MASK = c_uint.in_dll(libflac, "FLAC__SUBFRAME_TYPE_LPC_BYTE_ALIGNED_MASK")


    FLAC__ChannelAssignment = c_int

    FLAC__CHANNEL_ASSIGNMENT_INDEPENDENT = 0
    FLAC__CHANNEL_ASSIGNMENT_LEFT_SIDE = 1
    FLAC__CHANNEL_ASSIGNMENT_RIGHT_SIDE = 2
    FLAC__CHANNEL_ASSIGNMENT_MID_SIDE = 3



    libflac.FLAC__ChannelAssignmentString.restype = c_char_p
    libflac.FLAC__ChannelAssignmentString.argtypes = []

    def FLAC__ChannelAssignmentString():
        return libflac.FLAC__ChannelAssignmentString()

    FLAC__FrameNumberType = c_int


    libflac.FLAC__FrameNumberTypeString.restype = c_char_p
    libflac.FLAC__FrameNumberTypeString.argtypes = []

    def FLAC__FrameNumberTypeString():
        return libflac.FLAC__FrameNumberTypeString()


    class FLAC__FrameHeader_number(Union):
        _fields_ =[("frame_number", FLAC__uint32),
                   ("sample_number", FLAC__uint64)]

    class FLAC__FrameHeader(Structure):
        _fields_ = [("blocksize", c_uint),
                    ("sample_rate", c_uint),
                    ("channels", c_uint),
                    ("channel_assignment", FLAC__ChannelAssignment),
                    ("bits_per_sample", c_uint),
                    ("number_type", FLAC__FrameNumberType),
                    ("number", FLAC__FrameHeader_number),
                    ("crc", FLAC__uint8)]
        

    FLAC__FRAME_HEADER_SYNC = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_SYNC")

    FLAC__FRAME_HEADER_RESERVED_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_RESERVED_LEN")

    FLAC__FRAME_HEADER_BLOCKING_STRATEGY_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_BLOCKING_STRATEGY_LEN")

    FLAC__FRAME_HEADER_BLOCK_SIZE_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_BLOCK_SIZE_LEN")

    FLAC__FRAME_HEADER_SAMPLE_RATE_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_SAMPLE_RATE_LEN")

    FLAC__FRAME_HEADER_CHANNEL_ASSIGNMENT_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_CHANNEL_ASSIGNMENT_LEN")

    FLAC__FRAME_HEADER_BITS_PER_SAMPLE_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_BITS_PER_SAMPLE_LEN")

    FLAC__FRAME_HEADER_ZERO_PAD_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_ZERO_PAD_LEN")

    FLAC__FRAME_HEADER_CRC_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_HEADER_CRC_LEN")



    class FLAC__FrameFooter(Structure):
        _fields_ = [("crc", FLAC__uint16)]

    FLAC__FRAME_FOOTER_CRC_LEN = c_uint.in_dll(libflac, "FLAC__FRAME_FOOTER_CRC_LEN")



    class FLAC__Frame(Structure):
        _fields_ = [("header", FLAC__FrameHeader),
                    ("subframes", FLAC__Subframe * FLAC__MAX_CHANNELS),
                    ("footer", FLAC__FrameFooter)]
        

    FLAC__MetadataType = c_int

    FLAC__METADATA_TYPE_STREAMINFO = 0

    FLAC__METADATA_TYPE_PADDING = 1

    FLAC__METADATA_TYPE_APPLICATION = 2

    FLAC__METADATA_TYPE_SEEKTABLE = 3

    FLAC__METADATA_TYPE_VORBIS_COMMENT = 4

    FLAC__METADATA_TYPE_CUESHEET = 5

    FLAC__METADATA_TYPE_PICTURE = 6

    FLAC__METADATA_TYPE_UNDEFINED = 7

    FLAC__MAX_METADATA_TYPE = FLAC__MAX_METADATA_TYPE_CODE



    libflac.FLAC__MetadataTypeString.restype = c_char_p
    libflac.FLAC__MetadataTypeString.argtypes = []

    def FLAC__MetadataTypeString():
        return libflac.FLAC__MetadataTypeString()



    class FLAC__StreamMetadata_StreamInfo(Structure):
        _fields_ = [("min_blocksize", c_uint),
                    ("max_framesize", c_uint),
                    ("min_framesize", c_uint),
                    ("max_framesize", c_uint),
                    ("sample_rate", c_uint),
                    ("channels", c_uint),
                    ("bits_per_sample", c_uint),
                    ("total_samples", FLAC__uint64),
                    ("md5sum", FLAC__byte*16)]

    FLAC__STREAM_METADATA_STREAMINFO_MIN_BLOCK_SIZE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_MIN_BLOCK_SIZE_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_MAX_BLOCK_SIZE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_MAX_BLOCK_SIZE_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_MIN_FRAME_SIZE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_MIN_FRAME_SIZE_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_MAX_FRAME_SIZE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_MAX_FRAME_SIZE_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_SAMPLE_RATE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_SAMPLE_RATE_LEN")


    FLAC__STREAM_METADATA_STREAMINFO_CHANNELS_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_CHANNELS_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_BITS_PER_SAMPLE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_BITS_PER_SAMPLE_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_TOTAL_SAMPLES_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_TOTAL_SAMPLES_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_MD5SUM_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_STREAMINFO_MD5SUM_LEN")

    FLAC__STREAM_METADATA_STREAMINFO_LENGTH =(34)


    class FLAC__StreamMetadata_Padding(Structure):
        _fields_ = [("dummy", c_int)]



    class FLAC__StreamMetadata_Application(Structure):
        _fields_ = [("id", FLAC__byte*4),
                    ("data", FLAC__byte_p)]

    FLAC__STREAM_METADATA_APPLICATION_ID_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_APPLICATION_ID_LEN")
    

    class FLAC__StreamMetadata_SeekPoint(Structure):
        _fields_ = [("sample_number", FLAC__uint64),
                    ("stream_offset", FLAC__uint64),
                    ("frame_samples", c_uint)]

    FLAC__STREAM_METADATA_SEEKPOINT_SAMPLE_NUMBER_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_SEEKPOINT_SAMPLE_NUMBER_LEN")

    FLAC__STREAM_METADATA_SEEKPOINT_STREAM_OFFSET_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_SEEKPOINT_STREAM_OFFSET_LEN")

    FLAC__STREAM_METADATA_SEEKPOINT_FRAME_SAMPLES_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_SEEKPOINT_FRAME_SAMPLES_LEN")

    FLAC__STREAM_METADATA_SEEKPOINT_LENGTH =(18)


    FLAC__STREAM_METADATA_SEEKPOINT_PLACEHOLDER = FLAC__uint64.in_dll(libflac, "FLAC__STREAM_METADATA_SEEKPOINT_PLACEHOLDER")

    class FLAC__StreamMetadata_SeekTable(Structure):
        _fields_ = [("num_points", c_uint),
                    ("points", POINTER(FLAC__StreamMetadata_SeekPoint))]

    class FLAC__StreamMetadata_VorbisComment_Entry(Structure):
        _fields_ = [("length", FLAC__uint32),
                    ("entry", FLAC__byte_p)]

    FLAC__STREAM_METADATA_VORBIS_COMMENT_ENTRY_LENGTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_VORBIS_COMMENT_ENTRY_LENGTH_LEN")


    class FLAC__StreamMetadata_VorbisComment(Structure):
        _fields_ = [("vendor_string", FLAC__StreamMetadata_VorbisComment_Entry),
                    ("num_comments", FLAC__uint32),
                    ("comments", POINTER(FLAC__StreamMetadata_VorbisComment_Entry))]

    FLAC__STREAM_METADATA_VORBIS_COMMENT_NUM_COMMENTS_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_VORBIS_COMMENT_NUM_COMMENTS_LEN")


    class FLAC__StreamMetadata_CueSheet_Index(Structure):
        _fields_ = [("offset", FLAC__uint64),
                    ("number", FLAC__byte)]
        

    FLAC__STREAM_METADATA_CUESHEET_INDEX_OFFSET_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_INDEX_OFFSET_LEN")
    
    FLAC__STREAM_METADATA_CUESHEET_INDEX_NUMBER_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_INDEX_NUMBER_LEN")

    FLAC__STREAM_METADATA_CUESHEET_INDEX_RESERVED_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_INDEX_RESERVED_LEN")


    class FLAC__StreamMetadata_CueSheet_Track(Structure):
        _fields_ = [("offset", FLAC__uint64),
                    ("number", FLAC__byte),
                    ("isrc", c_char*13),
                    ("type", c_uint),
                    ("pre_emphasis", c_uint),
                    ("num_indices", FLAC__byte),
                    ("indices", POINTER(FLAC__StreamMetadata_CueSheet_Index))]

    FLAC__STREAM_METADATA_CUESHEET_TRACK_OFFSET_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_OFFSET_LEN")
    
    FLAC__STREAM_METADATA_CUESHEET_TRACK_NUMBER_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_NUMBER_LEN")

    FLAC__STREAM_METADATA_CUESHEET_TRACK_ISRC_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_ISRC_LEN")

    FLAC__STREAM_METADATA_CUESHEET_TRACK_TYPE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_TYPE_LEN")

    FLAC__STREAM_METADATA_CUESHEET_TRACK_PRE_EMPHASIS_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_PRE_EMPHASIS_LEN")

    FLAC__STREAM_METADATA_CUESHEET_TRACK_RESERVED_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_RESERVED_LEN")

    FLAC__STREAM_METADATA_CUESHEET_TRACK_NUM_INDICES_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_TRACK_NUM_INDICES_LEN")


    class FLAC__StreamMetadata_CueSheet(Structure):
        _fields_ = [("media_catalog_number", c_char*129),
                    ("lead_in", FLAC__uint64),
                    ("is_cd", FLAC__bool),
                    ("num_tracks", c_uint),
                    ("tracks", POINTER(FLAC__StreamMetadata_CueSheet_Track))]

    FLAC__STREAM_METADATA_CUESHEET_MEDIA_CATALOG_NUMBER_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_MEDIA_CATALOG_NUMBER_LEN")
        

    FLAC__STREAM_METADATA_CUESHEET_LEAD_IN_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_LEAD_IN_LEN")

    FLAC__STREAM_METADATA_CUESHEET_IS_CD_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_IS_CD_LEN")

    FLAC__STREAM_METADATA_CUESHEET_RESERVED_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_RESERVED_LEN")

    FLAC__STREAM_METADATA_CUESHEET_NUM_TRACKS_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_CUESHEET_NUM_TRACKS_LEN")


    FLAC__StreamMetadata_Picture_Type = c_int
    FLAC__STREAM_METADATA_PICTURE_TYPE_OTHER = 0
    FLAC__STREAM_METADATA_PICTURE_TYPE_FILE_ICON_STANDARD = 1
    FLAC__STREAM_METADATA_PICTURE_TYPE_FILE_ICON = 2
    FLAC__STREAM_METADATA_PICTURE_TYPE_FRONT_COVER = 3
    FLAC__STREAM_METADATA_PICTURE_TYPE_BACK_COVER = 4
    FLAC__STREAM_METADATA_PICTURE_TYPE_LEAFLET_PAGE = 5
    FLAC__STREAM_METADATA_PICTURE_TYPE_MEDIA = 6
    FLAC__STREAM_METADATA_PICTURE_TYPE_LEAD_ARTIST = 7
    FLAC__STREAM_METADATA_PICTURE_TYPE_ARTIST = 8
    FLAC__STREAM_METADATA_PICTURE_TYPE_CONDUCTOR = 9
    FLAC__STREAM_METADATA_PICTURE_TYPE_BAND = 10
    FLAC__STREAM_METADATA_PICTURE_TYPE_COMPOSER = 11
    FLAC__STREAM_METADATA_PICTURE_TYPE_LYRICIST = 12
    FLAC__STREAM_METADATA_PICTURE_TYPE_RECORDING_LOCATION = 13
    FLAC__STREAM_METADATA_PICTURE_TYPE_DURING_RECORDING = 14
    FLAC__STREAM_METADATA_PICTURE_TYPE_DURING_PERFORMANCE = 15
    FLAC__STREAM_METADATA_PICTURE_TYPE_VIDEO_SCREEN_CAPTURE = 16
    FLAC__STREAM_METADATA_PICTURE_TYPE_FISH = 17
    FLAC__STREAM_METADATA_PICTURE_TYPE_ILLUSTRATION = 18
    FLAC__STREAM_METADATA_PICTURE_TYPE_BAND_LOGOTYPE = 19
    FLAC__STREAM_METADATA_PICTURE_TYPE_PUBLISHER_LOGOTYPE = 20


    libflac.FLAC__StreamMetadata_Picture_TypeString.restype = c_char_p
    libflac.FLAC__StreamMetadata_Picture_TypeString.argtypes = []

    def FLAC__StreamMetadata_Picture_TypeString():
        return libflac.FLAC__StreamMetadata_Picture_TypeString()


    class FLAC__StreamMetadata_Picture(Structure):
        _fields_ = [("type", FLAC__StreamMetadata_Picture_Type),
                    ("mime_type", c_char_p),
                    ("description", FLAC__byte_p),
                    ("width", FLAC__uint32),
                    ("height", FLAC__uint32),
                    ("depth", FLAC__uint32),
                    ("colors", FLAC__uint32),
                    ("data_length", FLAC__uint32),
                    ("data", FLAC__byte)]

    FLAC__STREAM_METADATA_PICTURE_TYPE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_TYPE_LEN")

    FLAC__STREAM_METADATA_PICTURE_MIME_TYPE_LENGTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_MIME_TYPE_LENGTH_LEN")

    FLAC__STREAM_METADATA_PICTURE_DESCRIPTION_LENGTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_DESCRIPTION_LENGTH_LEN")

    FLAC__STREAM_METADATA_PICTURE_WIDTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_WIDTH_LEN")

    FLAC__STREAM_METADATA_PICTURE_HEIGHT_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_HEIGHT_LEN")


    FLAC__STREAM_METADATA_PICTURE_DEPTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_DEPTH_LEN")

    FLAC__STREAM_METADATA_PICTURE_COLORS_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_COLORS_LEN")

    FLAC__STREAM_METADATA_PICTURE_DATA_LENGTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_PICTURE_DATA_LENGTH_LEN")  


    class FLAC__StreamMetadata_Unknown(Structure):
        _fields_ = [("data", FLAC__byte_p)]


    class FLAC__StreamMetadata_data(Union):
        _fields_ = [("stream_info", FLAC__StreamMetadata_StreamInfo),
                    ("padding", FLAC__StreamMetadata_Padding),
                    ("application", FLAC__StreamMetadata_Application),
                    ("seek_table", FLAC__StreamMetadata_SeekTable),
                    ("vorbis_comment", FLAC__StreamMetadata_VorbisComment),
                    ("cue_sheet", FLAC__StreamMetadata_CueSheet),
                    ("picture", FLAC__StreamMetadata_Picture),
                    ("unknown", FLAC__StreamMetadata_Unknown)]

    class FLAC__StreamMetadata(Structure):
        _fields_ = [("type", FLAC__MetadataType),
                    ("is_last", FLAC__bool),
                    ("length", c_uint),
                    ("data", FLAC__StreamMetadata_data)]

    FLAC__STREAM_METADATA_IS_LAST_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_IS_LAST_LEN")
        
    FLAC__STREAM_METADATA_TYPE_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_TYPE_LEN")

    FLAC__STREAM_METADATA_LENGTH_LEN = c_uint.in_dll(libflac, "FLAC__STREAM_METADATA_LENGTH_LEN")

    FLAC__STREAM_METADATA_HEADER_LENGTH =(4)



    libflac.FLAC__format_sample_rate_is_valid.restype = FLAC__bool
    libflac.FLAC__format_sample_rate_is_valid.argtypes = [c_uint]

    def FLAC__format_sample_rate_is_valid(sample_rate):
        return libflac.FLAC__format_sample_rate_is_valid(sample_rate)


    libflac.FLAC__format_blocksize_is_subset.restype = FLAC__bool
    libflac.FLAC__format_blocksize_is_subset.argtypes = [c_uint, c_uint]

    def FLAC__format_blocksize_is_subset(blocksize, sample_rate):
        return libflac.FLAC__format_blocksize_is_subset(blocksize, sample_rate)


    libflac.FLAC__format_sample_rate_is_subset.restype = FLAC__bool
    libflac.FLAC__format_sample_rate_is_subset.argtypes = [c_uint]

    def FLAC__format_sample_rate_is_subset(sample_rate):
        return libflac.FLAC__format_sample_rate_is_subset(sample_rate)


    libflac.FLAC__format_vorbiscomment_entry_name_is_legal.restype = FLAC__bool
    libflac.FLAC__format_vorbiscomment_entry_name_is_legal.argtypes = [c_char_p]

    def FLAC__format_vorbiscomment_entry_name_is_legal(name):
        return libflac.FLAC__format_vorbiscomment_entry_name_is_legal(name)

    libflac.FLAC__format_vorbiscomment_entry_value_is_legal.restype = FLAC__bool
    libflac.FLAC__format_vorbiscomment_entry_value_is_legal.argtypes = [FLAC__byte_p, c_uint]

    def FLAC__format_vorbiscomment_entry_value_is_legal(value, length):
        return libflac.FLAC__format_vorbiscomment_entry_value_is_legal(value, length)

    libflac.FLAC__format_vorbiscomment_entry_is_legal.restype = FLAC__bool
    libflac.FLAC__format_vorbiscomment_entry_is_legal.argtypes = [FLAC__byte_p, c_uint]

    def FLAC__format_vorbiscomment_entry_is_legal(entry, length):
        return libflac.FLAC__format_vorbiscomment_entry_is_legal(entry, length)

    libflac.FLAC__format_seektable_is_legal.restype = FLAC__bool
    libflac.FLAC__format_seektable_is_legal.argtypes = [POINTER(FLAC__StreamMetadata_SeekTable)]

    def FLAC__format_seektable_is_legal(seek_table):
        return libflac.FLAC__format_seektable_is_legal(seek_table)


    libflac.FLAC__format_seektable_sort.restype = FLAC__bool
    libflac.FLAC__format_seektable_sort.argtypes = [POINTER(FLAC__StreamMetadata_SeekTable)]

    def FLAC__format_seektable_sort(seek_table):
        return libflac.FLAC__format_seektable_sort(seek_table)

    libflac.FLAC__format_cuesheet_is_legal.restype = FLAC__bool
    libflac.FLAC__format_cuesheet_is_legal.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet), FLAC__bool, c_char_p_p]

    def FLAC__format_cuesheet_is_legal(cue_sheet, check_cd_da_subset, violation):
        return libflac.FLAC__format_cuesheet_is_legal(cue_sheet, check_cd_da_subset, violation)

    # /format

    # metadata

    libflac.FLAC__metadata_get_streaminfo.restype = FLAC__bool
    libflac.FLAC__metadata_get_streaminfo.argtypes = [c_char_p, POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_get_streaminfo(filename, streaminfo):
        return libflac.FLAC__metadata_get_streaminfo(filename, streaminfo)

    libflac.FLAC__metadata_get_tags.restype = FLAC__bool
    libflac.FLAC__metadata_get_tags.argtypes = [c_char_p, POINTER(POINTER(FLAC__StreamMetadata))]

    def FLAC__metadata_get_tags(filename, tags):
        return libflac.FLAC__metadata_get_tags(filename, tags)

    libflac.FLAC__metadata_get_cuesheet.restype = FLAC__bool
    libflac.FLAC__metadata_get_cuesheet.argtypes = [c_char_p, POINTER(POINTER(FLAC__StreamMetadata))]

    def FLAC__metadata_get_cuesheet(filename, cuesheet):
        return libflac.FLAC__metadata_get_cuesheet(filename, cuesheet)

    libflac.FLAC__metadata_get_picture.restype = FLAC__bool
    libflac.FLAC__metadata_get_picture.argtypes = [c_char_p, POINTER(POINTER(FLAC__StreamMetadata)), FLAC__StreamMetadata_Picture_Type, c_char_p, FLAC__byte_p, c_uint, c_uint, c_uint, c_uint]

    def FLAC__metadata_get_picture(filename, picture, type, mime_type, description, max_width, max_height, max_depth, max_colors):
        return libflac.FLAC__metadata_get_picture(filename, picture, type, mime_type, description, max_width, max_height, max_depth, max_colors)


    class FLAC__Metadata_SimpleIterator(Structure):
        _fields_ = [("dummy", c_int)]

    FLAC__Metadata_SimpleIteratorStatus = c_int

    FLAC__METADATA_SIMPLE_ITERATOR_STATUS_OK = 0


    libflac.FLAC__Metadata_SimpleIteratorStatusString.restype = c_char_p
    libflac.FLAC__Metadata_SimpleIteratorStatusString.argtypes = []

    def FLAC__Metadata_SimpleIteratorStatusString():
        return libflac.FLAC__Metadata_SimpleIteratorStatusString()


    libflac.FLAC__metadata_simple_iterator_new.restype = POINTER(FLAC__Metadata_SimpleIterator)
    libflac.FLAC__metadata_simple_iterator_new.argtypes = []

    def FLAC__metadata_simple_iterator_new():
        return libflac.FLAC__metadata_simple_iterator_new()


    libflac.FLAC__metadata_simple_iterator_delete.restype = None
    libflac.FLAC__metadata_simple_iterator_delete.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_delete(iterator):
        return libflac.FLAC__metadata_simple_iterator_delete(iterator)


    libflac.FLAC__metadata_simple_iterator_status.restype = FLAC__Metadata_SimpleIteratorStatus
    libflac.FLAC__metadata_simple_iterator_status.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_status(iterator):
        return libflac.FLAC__metadata_simple_iterator_status(iterator)

    libflac.FLAC__metadata_simple_iterator_init.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_init.argtypes = [POINTER(FLAC__Metadata_SimpleIterator), c_char_p, FLAC__bool, FLAC__bool]

    def FLAC__metadata_simple_iterator_init(iterator, filename, read_only, preserve_file_stats):
        return libflac.FLAC__metadata_simple_iterator_init(iterator, filename, read_only, preserve_file_stats)

    libflac.FLAC__metadata_simple_iterator_is_writable.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_is_writable.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_is_writable(iterator):
        return libflac.FLAC__metadata_simple_iterator_is_writable(iterator)

    libflac.FLAC__metadata_simple_iterator_next.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_next.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_next(iterator):
        return libflac.FLAC__metadata_simple_iterator_next(iterator)

    libflac.FLAC__metadata_simple_iterator_prev.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_prev.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_prev(iterator):
        return libflac.FLAC__metadata_simple_iterator_prev(iterator)

    libflac.FLAC__metadata_simple_iterator_is_last.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_is_last.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_is_last(iterator):
        return libflac.FLAC__metadata_simple_iterator_is_last(iterator)

    libflac.FLAC__metadata_simple_iterator_get_block_offset.restype = c_off_t
    libflac.FLAC__metadata_simple_iterator_get_block_offset.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_get_block_offset(iterator):
        return libflac.FLAC__metadata_simple_iterator_get_block_offset(iterator)

    libflac.FLAC__metadata_simple_iterator_get_block_type.restype = FLAC__MetadataType
    libflac.FLAC__metadata_simple_iterator_get_block_type.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_get_block_type(iterator):
        return libflac.FLAC__metadata_simple_iterator_get_block_type(iterator)

    libflac.FLAC__metadata_simple_iterator_get_block_length.restype = c_uint
    libflac.FLAC__metadata_simple_iterator_get_block_length.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_get_block_length(iterator):
        return libflac.FLAC__metadata_simple_iterator_get_block_length(iterator)

    libflac.FLAC__metadata_simple_iterator_get_application_id.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_get_application_id.argtypes = [POINTER(FLAC__Metadata_SimpleIterator), FLAC__byte_p]

    def FLAC__metadata_simple_iterator_get_application_id(iterator, id):
        return libflac.FLAC__metadata_simple_iterator_get_application_id(iterator, id)

    libflac.FLAC__metadata_simple_iterator_get_block.restype = POINTER(FLAC__StreamMetadata)
    libflac.FLAC__metadata_simple_iterator_get_block.argtypes = [POINTER(FLAC__Metadata_SimpleIterator)]

    def FLAC__metadata_simple_iterator_get_block(iterator):
        return libflac.FLAC__metadata_simple_iterator_get_block(iterator)
     
    libflac.FLAC__metadata_simple_iterator_set_block.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_set_block.argtypes = [POINTER(FLAC__Metadata_SimpleIterator), POINTER(FLAC__StreamMetadata), FLAC__bool]

    def FLAC__metadata_simple_iterator_set_block(iterator, block, use_padding):
        return libflac.FLAC__metadata_simple_iterator_set_block(iterator, block, use_padding)

    libflac.FLAC__metadata_simple_iterator_insert_block_after.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_insert_block_after.argtypes = [POINTER(FLAC__Metadata_SimpleIterator), POINTER(FLAC__StreamMetadata), FLAC__bool]

    def FLAC__metadata_simple_iterator_insert_block_after(iterator, block, use_padding):
        return libflac.FLAC__metadata_simple_iterator_insert_block_after(iterator, block, use_padding)

    libflac.FLAC__metadata_simple_iterator_delete_block.restype = FLAC__bool
    libflac.FLAC__metadata_simple_iterator_delete_block.argtypes = [POINTER(FLAC__Metadata_SimpleIterator), FLAC__bool]

    def FLAC__metadata_simple_iterator_delete_block(iterator, use_padding):
        return libflac.FLAC__metadata_simple_iterator_delete_block(iterator, use_padding)

    class FLAC__Metadata_Chain(Structure):
        _fields_ = [("dummy", c_int)]
        
    class FLAC__Metadata_Iterator(Structure):
        _fields_ = [("dummy", c_int)]

    FLAC__Metadata_ChainStatus = c_int

    FLAC__METADATA_CHAIN_STATUS_OK = 0

    libflac.FLAC__Metadata_ChainStatusString.restype = c_char_p
    libflac.FLAC__Metadata_ChainStatusString.argtypes = []

    def FLAC__Metadata_ChainStatusString():
        return libflac.FLAC__Metadata_ChainStatusString()

    libflac.FLAC__metadata_chain_new.restype = POINTER(FLAC__Metadata_Chain)
    libflac.FLAC__metadata_chain_new.argtypes = []

    def FLAC__metadata_chain_new():
        return libflac.FLAC__metadata_chain_new()

    libflac.FLAC__metadata_chain_delete.restype = None
    libflac.FLAC__metadata_chain_delete.argtypes = [POINTER(FLAC__Metadata_Chain)]

    def FLAC__metadata_chain_delete(chain):
        return libflac.FLAC__metadata_chain_delete(chain)

    libflac.FLAC__metadata_chain_status.restype = FLAC__Metadata_ChainStatus
    libflac.FLAC__metadata_chain_status.argtypes = [POINTER(FLAC__Metadata_Chain)]

    def FLAC__metadata_chain_status(chain):
        return libflac.FLAC__metadata_chain_status(chain)

    libflac.FLAC__metadata_chain_read.restype = FLAC__bool
    libflac.FLAC__metadata_chain_read.argtypes = [POINTER(FLAC__Metadata_Chain), c_char_p]

    def FLAC__metadata_chain_read(chain, filename):
        return libflac.FLAC__metadata_chain_read(chain, filename)

    libflac.FLAC__metadata_chain_read_ogg.restype = FLAC__bool
    libflac.FLAC__metadata_chain_read_ogg.argtypes = [POINTER(FLAC__Metadata_Chain), c_char_p]

    def FLAC__metadata_chain_read_ogg(chain, filename):
        return libflac.FLAC__metadata_chain_read_ogg(chain, filename)

    libflac.FLAC__metadata_chain_read_with_callbacks.restype = FLAC__bool
    libflac.FLAC__metadata_chain_read_with_callbacks.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__IOHandle, FLAC__IOCallbacks]

    def FLAC__metadata_chain_read_with_callbacks(chain, handle, callbacks):
        return libflac.FLAC__metadata_chain_read_with_callbacks(chain, handle, callbacks)

    libflac.FLAC__metadata_chain_read_ogg_with_callbacks.restype = FLAC__bool
    libflac.FLAC__metadata_chain_read_ogg_with_callbacks.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__IOHandle, FLAC__IOCallbacks]

    def FLAC__metadata_chain_read_ogg_with_callbacks(chain, handle, callbacks):
        return libflac.FLAC__metadata_chain_read_ogg_with_callbacks(chain, handle, callbacks)

    libflac.FLAC__metadata_chain_check_if_tempfile_needed.restype = FLAC__bool
    libflac.FLAC__metadata_chain_check_if_tempfile_needed.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__bool]

    def FLAC__metadata_chain_check_if_tempfile_needed(chain, use_padding):
        return libflac.FLAC__metadata_chain_check_if_tempfile_needed(chain, use_padding)

    libflac.FLAC__metadata_chain_write.restype = FLAC__bool
    libflac.FLAC__metadata_chain_write.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__bool, FLAC__bool]

    def FLAC__metadata_chain_write(chain, use_padding, preserve_file_stats):
        return libflac.FLAC__metadata_chain_write(chain, use_padding, preserve_file_stats)

    libflac.FLAC__metadata_chain_write_with_callbacks.restype = FLAC__bool
    libflac.FLAC__metadata_chain_write_with_callbacks.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__bool, FLAC__IOHandle, FLAC__IOCallbacks]

    def FLAC__metadata_chain_write_with_callbacks(chain, use_padding, handle, callbacks):
        return libflac.FLAC__metadata_chain_write_with_callbacks(chain, use_padding, handle, callbacks)

    libflac.FLAC__metadata_chain_write_with_callbacks_and_tempfile.restype = FLAC__bool
    libflac.FLAC__metadata_chain_write_with_callbacks_and_tempfile.argtypes = [POINTER(FLAC__Metadata_Chain), FLAC__bool, FLAC__IOHandle, FLAC__IOCallbacks, FLAC__IOHandle, FLAC__IOCallbacks]

    def FLAC__metadata_chain_write_with_callbacks_and_tempfile(chain, use_padding, handle, callbacks, temp_handle, temp_callbacks):
        return libflac.FLAC__metadata_chain_write_with_callbacks_and_tempfile(chain, use_padding, handle, callbacks, temp_handle, temp_callbacks)

    libflac.FLAC__metadata_chain_merge_padding.restype = None
    libflac.FLAC__metadata_chain_merge_padding.argtypes = [POINTER(FLAC__Metadata_Chain)]

    def FLAC__metadata_chain_merge_padding(chain):
        return libflac.FLAC__metadata_chain_merge_padding(chain)

    libflac.FLAC__metadata_chain_sort_padding.restype = None
    libflac.FLAC__metadata_chain_sort_padding.argtypes = [POINTER(FLAC__Metadata_Chain)]

    def FLAC__metadata_chain_sort_padding(chain):
        return libflac.FLAC__metadata_chain_sort_padding(chain)

    libflac.FLAC__metadata_iterator_new.restype = POINTER(FLAC__Metadata_Iterator)
    libflac.FLAC__metadata_iterator_new.argtypes = []

    def FLAC__metadata_iterator_new():
        return libflac.FLAC__metadata_iterator_new()

    libflac.FLAC__metadata_iterator_delete.restype = None
    libflac.FLAC__metadata_iterator_delete.argtypes = [POINTER(FLAC__Metadata_Iterator)]

    def FLAC__metadata_iterator_delete(iterator):
        return libflac.FLAC__metadata_iterator_delete(iterator)

    libflac.FLAC__metadata_iterator_init.restype = None
    libflac.FLAC__metadata_iterator_init.argtypes = [POINTER(FLAC__Metadata_Iterator), POINTER(FLAC__Metadata_Chain)]

    def FLAC__metadata_iterator_init(iterator, chain):
        return libflac.FLAC__metadata_iterator_init(iterator, chain)

    libflac.FLAC__metadata_iterator_next.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_next.argtypes = [POINTER(FLAC__Metadata_Iterator)]

    def FLAC__metadata_iterator_next(iterator):
        return libflac.FLAC__metadata_iterator_next(iterator)

    libflac.FLAC__metadata_iterator_prev.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_prev.argtypes = [POINTER(FLAC__Metadata_Iterator)]

    def FLAC__metadata_iterator_prev(iterator):
        return libflac.FLAC__metadata_iterator_prev(iterator)

    libflac.FLAC__metadata_iterator_get_block_type.restype = FLAC__MetadataType
    libflac.FLAC__metadata_iterator_get_block_type.argtypes = [POINTER(FLAC__Metadata_Iterator)]

    def FLAC__metadata_iterator_get_block_type(iterator):
        return libflac.FLAC__metadata_iterator_get_block_type(iterator)

    libflac.FLAC__metadata_iterator_get_block_type.restype = POINTER(FLAC__StreamMetadata)
    libflac.FLAC__metadata_iterator_get_block_type.argtypes = [POINTER(FLAC__Metadata_Iterator)]

    def FLAC__metadata_iterator_get_block_type(iterator):
        return libflac.FLAC__metadata_iterator_get_block_type(iterator)

    libflac.FLAC__metadata_iterator_set_block.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_set_block.argtypes = [POINTER(FLAC__Metadata_Iterator), POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_iterator_set_block(iterator, block):
        return libflac.FLAC__metadata_iterator_set_block(iterator, block)

    libflac.FLAC__metadata_iterator_delete_block.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_delete_block.argtypes = [POINTER(FLAC__Metadata_Iterator), FLAC__bool]

    def FLAC__metadata_iterator_delete_block(iterator, replace_with_padding):
        return libflac.FLAC__metadata_iterator_delete_block(iterator, replace_with_padding)

    libflac.FLAC__metadata_iterator_insert_block_before.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_insert_block_before.argtypes = [POINTER(FLAC__Metadata_Iterator), POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_iterator_insert_block_before(iterator, block):
        return libflac.FLAC__metadata_iterator_insert_block_before(iterator, block)

    libflac.FLAC__metadata_iterator_insert_block_after.restype = FLAC__bool
    libflac.FLAC__metadata_iterator_insert_block_after.argtypes = [POINTER(FLAC__Metadata_Iterator), POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_iterator_insert_block_after(iterator, block):
        return libflac.FLAC__metadata_iterator_insert_block_after(iterator, block)

    libflac.FLAC__metadata_object_new.restype = POINTER(FLAC__StreamMetadata)
    libflac.FLAC__metadata_object_new.argtypes = [POINTER(FLAC__MetadataType)]

    def FLAC__metadata_object_new(type):
        return libflac.FLAC__metadata_object_new(type)

    libflac.FLAC__metadata_object_clone.restype = POINTER(FLAC__StreamMetadata)
    libflac.FLAC__metadata_object_clone.argtypes = [POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_object_clone(object):
        return libflac.FLAC__metadata_object_clone(object)

    libflac.FLAC__metadata_object_delete.restype = None
    libflac.FLAC__metadata_object_delete.argtypes = [POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_object_delete(object):
        return libflac.FLAC__metadata_object_delete(object)

    libflac.FLAC__metadata_object_is_equal.restype = FLAC__bool
    libflac.FLAC__metadata_object_is_equal.argtypes = [POINTER(FLAC__StreamMetadata), POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_object_is_equal(block1, block2):
        return libflac.FLAC__metadata_object_is_equal(block1, block2)

    libflac.FLAC__metadata_object_application_set_data.restype = FLAC__bool
    libflac.FLAC__metadata_object_application_set_data.argtypes = [POINTER(FLAC__StreamMetadata), FLAC__byte_p, c_uint, FLAC__bool]

    def FLAC__metadata_object_application_set_data(object, data, length, copy):
        return libflac.FLAC__metadata_object_application_set_data(object, data, length, copy)

    libflac.FLAC__metadata_object_seektable_resize_points.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_resize_points.argtypes = [POINTER(FLAC__StreamMetadata),c_uint]

    def FLAC__metadata_object_seektable_resize_points(object, new_num_points):
        return libflac.FLAC__metadata_object_seektable_resize_points(object, new_num_points)

    libflac.FLAC__metadata_object_seektable_set_point.restype = None
    libflac.FLAC__metadata_object_seektable_set_point.argtypes = [POINTER(FLAC__StreamMetadata),c_uint, FLAC__StreamMetadata_SeekPoint]

    def FLAC__metadata_object_seektable_set_point(object, point_num, point):
        return libflac.FLAC__metadata_object_seektable_set_point(object, point_num, point)

    libflac.FLAC__metadata_object_seektable_insert_point.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_insert_point.argtypes = [POINTER(FLAC__StreamMetadata),c_uint, FLAC__StreamMetadata_SeekPoint]

    def FLAC__metadata_object_seektable_insert_point(object, point_num, point):
        return libflac.FLAC__metadata_object_seektable_insert_point(object, point_num, point)

    libflac.FLAC__metadata_object_seektable_delete_point.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_delete_point.argtypes = [POINTER(FLAC__StreamMetadata),c_uint]

    def FLAC__metadata_object_seektable_delete_point(object, point_num):
        return libflac.FLAC__metadata_object_seektable_delete_point(object, point_num)

    libflac.FLAC__metadata_object_seektable_is_legal.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_is_legal.argtypes = [POINTER(FLAC__StreamMetadata)]

    def FLAC__metadata_object_seektable_is_legal(object):
        return libflac.FLAC__metadata_object_seektable_is_legal(object)

    libflac.FLAC__metadata_object_seektable_template_append_placeholders.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_append_placeholders.argtypes = [POINTER(FLAC__StreamMetadata), c_uint]

    def FLAC__metadata_object_seektable_template_append_placeholders(object, num):
        return libflac.FLAC__metadata_object_seektable_template_append_placeholders(object, num)

    libflac.FLAC__metadata_object_seektable_template_append_point.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_append_point.argtypes = [POINTER(FLAC__StreamMetadata), FLAC__uint64]

    def FLAC__metadata_object_seektable_template_append_point(object, sample_number):
        return libflac.FLAC__metadata_object_seektable_template_append_point(object, sample_number)

    libflac.FLAC__metadata_object_seektable_template_append_points.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_append_points.argtypes = [POINTER(FLAC__StreamMetadata), POINTER(FLAC__uint64*0), c_uint]

    def FLAC__metadata_object_seektable_template_append_points(object, sample_numbers, num):
        return libflac.FLAC__metadata_object_seektable_template_append_points(object, sample_numbers, num)

    libflac.FLAC__metadata_object_seektable_template_append_spaced_points.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_append_spaced_points.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__uint64]

    def FLAC__metadata_object_seektable_template_append_spaced_points(object, num, total_samples):
        return libflac.FLAC__metadata_object_seektable_template_append_spaced_points(object, num, total_samples)

    libflac.FLAC__metadata_object_seektable_template_append_spaced_points_by_samples.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_append_spaced_points_by_samples.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__uint64]

    def FLAC__metadata_object_seektable_template_append_spaced_points_by_samples(object, samples, total_samples):
        return libflac.FLAC__metadata_object_seektable_template_append_spaced_points_by_samples(object, samples, total_samples)

    libflac.FLAC__metadata_object_seektable_template_sort.restype = FLAC__bool
    libflac.FLAC__metadata_object_seektable_template_sort.argtypes = [POINTER(FLAC__StreamMetadata), FLAC__bool]

    def FLAC__metadata_object_seektable_template_sort(object, compact):
        return libflac.FLAC__metadata_object_seektable_template_sort(object, compact)

    libflac.FLAC__metadata_object_vorbiscomment_set_vendor_string.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_set_vendor_string.argtypes = [POINTER(FLAC__StreamMetadata), FLAC__StreamMetadata_VorbisComment_Entry, FLAC__bool]

    def FLAC__metadata_object_vorbiscomment_set_vendor_string(object, entry, copy):
        return libflac.FLAC__metadata_object_vorbiscomment_set_vendor_string(object, entry, copy)

    libflac.FLAC__metadata_object_vorbiscomment_resize_comments.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_resize_comments.argtypes = [POINTER(FLAC__StreamMetadata), c_uint]

    def FLAC__metadata_object_vorbiscomment_resize_comments(object, new_num_comments):
        return libflac.FLAC__metadata_object_vorbiscomment_resize_comments(object, new_num_comments)

    libflac.FLAC__metadata_object_vorbiscomment_set_comment.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_set_comment.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__StreamMetadata_VorbisComment_Entry, FLAC__bool]

    def FLAC__metadata_object_vorbiscomment_set_comment(object, comment_num, entry, copy):
        return libflac.FLAC__metadata_object_vorbiscomment_set_comment(object, comment_num, entry, copy)

    libflac.FLAC__metadata_object_vorbiscomment_insert_comment.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_insert_comment.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__StreamMetadata_VorbisComment_Entry, FLAC__bool]

    def FLAC__metadata_object_vorbiscomment_insert_comment(object, comment_num, entry, copy):
        return libflac.FLAC__metadata_object_vorbiscomment_insert_comment(object, comment_num, entry, copy)

    libflac.FLAC__metadata_object_vorbiscomment_append_comment.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_append_comment.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__StreamMetadata_VorbisComment_Entry, FLAC__bool]

    def FLAC__metadata_object_vorbiscomment_append_comment(object, entry, copy):
        return libflac.FLAC__metadata_object_vorbiscomment_append_comment(object,entry, copy)

    libflac.FLAC__metadata_object_vorbiscomment_replace_comment.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_replace_comment.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, FLAC__StreamMetadata_VorbisComment_Entry, FLAC__bool, FLAC__bool]

    def FLAC__metadata_object_vorbiscomment_replace_comment(object, entry, all, copy):
        return libflac.FLAC__metadata_object_vorbiscomment_replace_comment(object,entry, all, copy)

    libflac.FLAC__metadata_object_vorbiscomment_delete_comment.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_delete_comment.argtypes = [POINTER(FLAC__StreamMetadata), c_uint]

    def FLAC__metadata_object_vorbiscomment_delete_comment(object, comment_num):
        return libflac.FLAC__metadata_object_vorbiscomment_delete_comment(object,comment_num)

    libflac.FLAC__metadata_object_vorbiscomment_entry_from_name_value_pair.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_entry_from_name_value_pair.argtypes = [POINTER(FLAC__StreamMetadata_VorbisComment_Entry), c_char_p, c_char_p]

    def FLAC__metadata_object_vorbiscomment_entry_from_name_value_pair(entry, field_name, field_value):
        return libflac.FLAC__metadata_object_vorbiscomment_entry_from_name_value_pair(entry, field_name, field_value)

    libflac.FLAC__metadata_object_vorbiscomment_entry_to_name_value_pair.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_entry_to_name_value_pair.argtypes = [POINTER(FLAC__StreamMetadata_VorbisComment_Entry), c_char_p_p, c_char_p_p]

    def FLAC__metadata_object_vorbiscomment_entry_to_name_value_pair(entry, field_name, field_value):
        return libflac.FLAC__metadata_object_vorbiscomment_entry_to_name_value_pair(entry, field_name, field_value)

    libflac.FLAC__metadata_object_vorbiscomment_entry_matches.restype = FLAC__bool
    libflac.FLAC__metadata_object_vorbiscomment_entry_matches.argtypes = [POINTER(FLAC__StreamMetadata_VorbisComment_Entry), c_char_p, c_uint]

    def FLAC__metadata_object_vorbiscomment_entry_matches(entry, field_name, field_value):
        return libflac.FLAC__metadata_object_vorbiscomment_entry_matches(entry, field_name, field_value)

    libflac.FLAC__metadata_object_vorbiscomment_find_entry_from.restype = c_int
    libflac.FLAC__metadata_object_vorbiscomment_find_entry_from.argtypes = [POINTER(FLAC__StreamMetadata), c_uint, c_char_p]

    def FLAC__metadata_object_vorbiscomment_find_entry_from(object, offset, field_name):
        return libflac.FLAC__metadata_object_vorbiscomment_find_entry_from(object, offset, field_name)

    libflac.FLAC__metadata_object_vorbiscomment_remove_entry_matching.restype = c_int
    libflac.FLAC__metadata_object_vorbiscomment_remove_entry_matching.argtypes = [POINTER(FLAC__StreamMetadata), c_char_p]

    def FLAC__metadata_object_vorbiscomment_remove_entry_matching(object, field_name):
        return libflac.FLAC__metadata_object_vorbiscomment_remove_entry_matching(object, field_name)

    libflac.FLAC__metadata_object_vorbiscomment_remove_entries_matching.restype = c_int
    libflac.FLAC__metadata_object_vorbiscomment_remove_entries_matching.argtypes = [POINTER(FLAC__StreamMetadata), c_char_p]

    def FLAC__metadata_object_vorbiscomment_remove_entries_matching(object, field_name):
        return libflac.FLAC__metadata_object_vorbiscomment_remove_entries_matching(object, field_name)

    libflac.FLAC__metadata_object_cuesheet_track_new.restype = POINTER(FLAC__StreamMetadata_CueSheet_Track)
    libflac.FLAC__metadata_object_cuesheet_track_new.argtypes = []

    def FLAC__metadata_object_cuesheet_track_new():
        return libflac.FLAC__metadata_object_cuesheet_track_new()

    libflac.FLAC__metadata_object_cuesheet_track_delete.restype = None
    libflac.FLAC__metadata_object_cuesheet_track_delete.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track)]

    def FLAC__metadata_object_cuesheet_track_delete(object):
        return libflac.FLAC__metadata_object_cuesheet_track_delete(object)

    libflac.FLAC__metadata_object_cuesheet_track_resize_indices.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_track_resize_indices.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, c_uint]

    def FLAC__metadata_object_cuesheet_track_resize_indices(object, track_num, new_num_indices):
        return libflac.FLAC__metadata_object_cuesheet_track_resize_indices(object, track_num, new_num_indices)

    libflac.FLAC__metadata_object_cuesheet_track_insert_index.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_track_insert_index.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, c_uint, FLAC__StreamMetadata_CueSheet_Index]

    def FLAC__metadata_object_cuesheet_track_insert_index(object, track_num, index_num, index):
        return libflac.FLAC__metadata_object_cuesheet_track_insert_index(object, track_num, index_num, index)

    libflac.FLAC__metadata_object_cuesheet_track_insert_blank_index.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_track_insert_blank_index.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, c_uint]

    def FLAC__metadata_object_cuesheet_track_insert_blank_index(object, track_num, index_num):
        return libflac.FLAC__metadata_object_cuesheet_track_insert_blank_index(object, track_num, index_num)

    libflac.FLAC__metadata_object_cuesheet_track_delete_index.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_track_delete_index.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, c_uint]

    def FLAC__metadata_object_cuesheet_track_delete_index(object, track_num, index_num):
        return libflac.FLAC__metadata_object_cuesheet_track_delete_index(object, track_num, index_num)

    libflac.FLAC__metadata_object_cuesheet_resize_tracks.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_resize_tracks.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint]

    def FLAC__metadata_object_cuesheet_resize_tracks(object, new_num_tracks):
        return libflac.FLAC__metadata_object_cuesheet_resize_tracks(object, new_num_tracks)

    libflac.FLAC__metadata_object_cuesheet_set_track.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_set_track.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, POINTER(FLAC__StreamMetadata_CueSheet_Track), FLAC__bool]

    def FLAC__metadata_object_cuesheet_set_track(object, new_num_tracks, track, copy):
        return libflac.FLAC__metadata_object_cuesheet_set_track(object, new_num_tracks, track, copy)

    libflac.FLAC__metadata_object_cuesheet_insert_track.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_insert_track.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint, POINTER(FLAC__StreamMetadata_CueSheet_Track), FLAC__bool]

    def FLAC__metadata_object_cuesheet_insert_track(object, track_num, track, copy):
        return libflac.FLAC__metadata_object_cuesheet_insert_track(object, track_num, track, copy)

    libflac.FLAC__metadata_object_cuesheet_insert_blank_track.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_insert_blank_track.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint]

    def FLAC__metadata_object_cuesheet_insert_blank_track(object, track_num):
        return libflac.FLAC__metadata_object_cuesheet_insert_blank_track(object, track_num)

    libflac.FLAC__metadata_object_cuesheet_delete_track.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_delete_track.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_uint]

    def FLAC__metadata_object_cuesheet_delete_track(object, track_num):
        return libflac.FLAC__metadata_object_cuesheet_delete_track(object, track_num)

    libflac.FLAC__metadata_object_cuesheet_is_legal.restype = FLAC__bool
    libflac.FLAC__metadata_object_cuesheet_is_legal.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), FLAC__bool, c_char_p_p]

    def FLAC__metadata_object_cuesheet_is_legal(object, check_cd_da_subset, violation):
        return libflac.FLAC__metadata_object_cuesheet_is_legal(object, check_cd_da_subset, violation)

    libflac.FLAC__metadata_object_cuesheet_calculate_cddb_id.restype = FLAC__uint32
    libflac.FLAC__metadata_object_cuesheet_calculate_cddb_id.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track)]

    def FLAC__metadata_object_cuesheet_calculate_cddb_id(object):
        return libflac.FLAC__metadata_object_cuesheet_calculate_cddb_id(object)

    libflac.FLAC__metadata_object_picture_set_mime_type.restype = FLAC__bool
    libflac.FLAC__metadata_object_picture_set_mime_type.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_char_p, FLAC__bool]

    def FLAC__metadata_object_picture_set_mime_type(object, mime_type, copy):
        return libflac.FLAC__metadata_object_picture_set_mime_type(object, mime_type, copy)

    libflac.FLAC__metadata_object_picture_set_description.restype = FLAC__bool
    libflac.FLAC__metadata_object_picture_set_description.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), FLAC__byte_p, FLAC__bool]

    def FLAC__metadata_object_picture_set_description(object, description, copy):
        return libflac.FLAC__metadata_object_picture_set_description(object, mime_type, copy)

    libflac.FLAC__metadata_object_picture_set_data.restype = FLAC__bool
    libflac.FLAC__metadata_object_picture_set_data.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), FLAC__byte_p,FLAC__uint32, FLAC__bool]

    def FLAC__metadata_object_picture_set_data(object, data, length, copy):
        return libflac.FLAC__metadata_object_picture_set_data(object, mime_type, copy)

    libflac.FLAC__metadata_object_picture_is_legal.restype = FLAC__bool
    libflac.FLAC__metadata_object_picture_is_legal.argtypes = [POINTER(FLAC__StreamMetadata_CueSheet_Track), c_char_p]

    def FLAC__metadata_object_picture_is_legal(object, violation):
        return libflac.FLAC__metadata_object_picture_is_legal(object, violation)

    # /metadata

    # stream_decoder

    FLAC__StreamDecoderState = c_int
    FLAC__StreamDecoderStateEnum = ["FLAC__STREAM_DECODER_SEARCH_FOR_METADATA",
                                    "FLAC__STREAM_DECODER_READ_METADATA",
                                    "FLAC__STREAM_DECODER_SEARCH_FOR_FRAME_SYNC",
                                    "FLAC__STREAM_DECODER_READ_FRAME", 
                                    "FLAC__STREAM_DECODER_END_OF_STREAM",
                                    "FLAC__STREAM_DECODER_OGG_ERROR",
                                    "FLAC__STREAM_DECODER_SEEK_ERROR",
                                    "FLAC__STREAM_DECODER_ABORTED", 
                                    "FLAC__STREAM_DECODER_MEMORY_ALLOCATION_ERROR",
                                    "FLAC__STREAM_DECODER_UNINITIALIZED"] 

    libflac.FLAC__StreamDecoderStateString.restype = c_char_p
    libflac.FLAC__StreamDecoderStateString.argtypes = []

    def FLAC__StreamDecoderStateString():
        return libflac.FLAC__StreamDecoderStateString()


    FLAC__StreamDecoderInitStatus = c_int
    FLAC__StreamDecoderInitStatusEnum = ["FLAC__STREAM_DECODER_INIT_STATUS_OK",
                                         "FLAC__STREAM_DECODER_INIT_STATUS_UNSUPPORTED_CONTAINER",
                                         "FLAC__STREAM_DECODER_INIT_STATUS_INVALID_CALLBACKS",
                                         "FLAC__STREAM_DECODER_INIT_STATUS_MEMORY_ALLOCATION_ERROR", 
                                         "FLAC__STREAM_DECODER_INIT_STATUS_ERROR_OPENING_FILE",
                                         "FLAC__STREAM_DECODER_INIT_STATUS_ALREADY_INITIALIZED"]

    libflac.FLAC__StreamDecoderInitStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderInitStatusString.argtypes = []

    def FLAC__StreamDecoderInitStatusString():
        return libflac.FLAC__StreamDecoderInitStatusString()


    FLAC__StreamDecoderReadStatus = c_int
    FLAC__StreamDecoderReadStatusEnum = ["FLAC__STREAM_DECODER_READ_STATUS_CONTINUE",
                                         "FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM",
                                         "FLAC__STREAM_DECODER_READ_STATUS_ABORT"]

    libflac.FLAC__StreamDecoderReadStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderReadStatusString.argtypes = []

    def FLAC__StreamDecoderReadStatusString():
        return libflac.FLAC__StreamDecoderReadStatusString()


    FLAC__StreamDecoderSeekStatus = c_int
    FLAC__StreamDecoderSeekStatusEnum = ["FLAC__STREAM_DECODER_SEEK_STATUS_OK",
                                         "FLAC__STREAM_DECODER_SEEK_STATUS_ERROR",
                                         "FLAC__STREAM_DECODER_SEEK_STATUS_UNSUPPORTED"]

    libflac.FLAC__StreamDecoderSeekStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderSeekStatusString.argtypes = []

    def FLAC__StreamDecoderSeekStatusString():
        return libflac.FLAC__StreamDecoderSeekStatusString()


    FLAC__StreamDecoderTellStatus = c_int
    FLAC__StreamDecoderTellStatusEnum = ["FLAC__STREAM_DECODER_TELL_STATUS_OK",
                                     "FLAC__STREAM_DECODER_TELL_STATUS_ERROR",
                                     "FLAC__STREAM_DECODER_TELL_STATUS_UNSUPPORTED"]

    libflac.FLAC__StreamDecoderTellStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderTellStatusString.argtypes = []

    def FLAC__StreamDecoderTellStatusString():
        return libflac.FLAC__StreamDecoderTellStatusString()


    FLAC__StreamDecoderLengthStatus = c_int
    FLAC__StreamDecoderLengthStatusEnum = ["FLAC__STREAM_DECODER_LENGTH_STATUS_OK",
                                       "FLAC__STREAM_DECODER_LENGTH_STATUS_ERROR",
                                       "FLAC__STREAM_DECODER_LENGTH_STATUS_UNSUPPORTED"]

    libflac.FLAC__StreamDecoderLengthStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderLengthStatusString.argtypes = []

    def FLAC__StreamDecoderLengthStatusString():
        return libflac.FLAC__StreamDecoderLengthStatusString()


    FLAC__StreamDecoderWriteStatus = c_int
    FLAC__StreamDecoderWriteStatusEnum = ["FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE", "FLAC__STREAM_DECODER_WRITE_STATUS_ABORT"]

    libflac.FLAC__StreamDecoderWriteStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderWriteStatusString.argtypes = []

    def FLAC__StreamDecoderWriteStatusString():
        return libflac.FLAC__StreamDecoderWriteStatusString()

    FLAC__StreamDecoderErrorStatus = c_int
    FLAC__StreamDecoderErrorStatusEnum = ["FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC",
                                      "FLAC__STREAM_DECODER_ERROR_STATUS_BAD_HEADER",
                                      "FLAC__STREAM_DECODER_ERROR_STATUS_FRAME_CRC_MISMATCH",
                                      "FLAC__STREAM_DECODER_ERROR_STATUS_UNPARSEABLE_STREAM"]

    libflac.FLAC__StreamDecoderErrorStatusString.restype = c_char_p
    libflac.FLAC__StreamDecoderErrorStatusString.argtypes = []

    def FLAC__StreamDecoderErrorStatusString():
        return libflac.FLAC__StreamDecoderErrorStatusString()



    class FLAC__StreamDecoderProtected(Structure):
        _fields_ = [("dummy", c_int)]

    class FLAC__StreamDecoderPrivate(Structure):
        _fields_ = [("dummy", c_int)]

    class FLAC__StreamDecoder(Structure):
        _fields_ = [("protected_", POINTER(FLAC__StreamDecoderProtected)),
                    ("private_", POINTER(FLAC__StreamDecoderPrivate))]

    FLAC__StreamDecoderReadCallback = CFUNCTYPE(
        FLAC__StreamDecoderReadStatus,
        POINTER(FLAC__StreamDecoder),
        POINTER(FLAC__byte*0),
        c_size_t_p,
        c_void_p
    )

    FLAC__StreamDecoderSeekCallback = CFUNCTYPE(
        FLAC__StreamDecoderSeekStatus,
        POINTER(FLAC__StreamDecoder),
        FLAC__uint64,
        c_void_p
    )

    FLAC__StreamDecoderTellCallback = CFUNCTYPE(
        FLAC__StreamDecoderTellStatus,
        POINTER(FLAC__StreamDecoder),
        FLAC__uint64_p,
        c_void_p
    )

    FLAC__StreamDecoderLengthCallback = CFUNCTYPE(
        FLAC__StreamDecoderLengthStatus,
        POINTER(FLAC__StreamDecoder),
        FLAC__uint64_p,
        c_void_p
    )

    FLAC__StreamDecoderEofCallback = CFUNCTYPE(
        FLAC__bool,
        POINTER(FLAC__StreamDecoder),
        c_void_p
    )

    FLAC__StreamDecoderWriteCallback = CFUNCTYPE(
        FLAC__StreamDecoderWriteStatus,
        POINTER(FLAC__StreamDecoder),
        POINTER(FLAC__Frame),
        POINTER(FLAC__int32_p*0),
        c_void_p
    )

    FLAC__StreamDecoderMetadataCallback = CFUNCTYPE(
        None,
        POINTER(FLAC__StreamDecoder),
        POINTER(FLAC__StreamMetadata),
        c_void_p
    )

    FLAC__StreamDecoderErrorCallback = CFUNCTYPE(
        None,
        POINTER(FLAC__StreamDecoder),
        FLAC__StreamDecoderErrorStatus,
        c_void_p
    )


    libflac.FLAC__stream_decoder_new.restype = POINTER(FLAC__StreamDecoder)
    libflac.FLAC__stream_decoder_new.argtypes = []

    def FLAC__stream_decoder_new():
        return libflac.FLAC__stream_decoder_new()

    libflac.FLAC__stream_decoder_delete.restype = None
    libflac.FLAC__stream_decoder_delete.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_delete(decoder):
        return libflac.FLAC__stream_decoder_delete(decoder)


    libflac.FLAC__stream_decoder_set_ogg_serial_number.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_ogg_serial_number.argtypes = [POINTER(FLAC__StreamDecoder), c_long]

    def FLAC__stream_decoder_set_ogg_serial_number(decoder, serial_number):
        return libflac.FLAC__stream_decoder_set_ogg_serial_number(decoder, serial_number)

    libflac.FLAC__stream_decoder_set_md5_checking.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_md5_checking.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__bool]

    def FLAC__stream_decoder_set_md5_checking(decoder, value):
        return libflac.FLAC__stream_decoder_set_md5_checking(decoder, value)

    libflac.FLAC__stream_decoder_set_metadata_respond.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_respond.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__MetadataType]

    def FLAC__stream_decoder_set_metadata_respond(decoder, type):
        return libflac.FLAC__stream_decoder_set_metadata_respond(decoder, type)

    libflac.FLAC__stream_decoder_set_metadata_respond_application.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_respond_application.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__byte*4]

    def FLAC__stream_decoder_set_metadata_respond_application(decoder, id):
        return libflac.FLAC__stream_decoder_set_metadata_respond_application(decoder, id)

    libflac.FLAC__stream_decoder_set_metadata_respond_all.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_respond_all.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_set_metadata_respond_all(decoder):
        return libflac.FLAC__stream_decoder_set_metadata_respond_all(decoder)

    libflac.FLAC__stream_decoder_set_metadata_ignore.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_ignore.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__MetadataType]

    def FLAC__stream_decoder_set_metadata_ignore(decoder, type):
        return libflac.FLAC__stream_decoder_set_metadata_ignore(decoder, type)

    libflac.FLAC__stream_decoder_set_metadata_ignore_application.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_ignore_application.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__byte*4]

    def FLAC__stream_decoder_set_metadata_ignore_application(decoder, id):
        return libflac.FLAC__stream_decoder_set_metadata_ignore_application(decoder, id)

    libflac.FLAC__stream_decoder_set_metadata_ignore_all.restype = FLAC__bool
    libflac.FLAC__stream_decoder_set_metadata_ignore_all.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_set_metadata_ignore_all(decoder):
        return libflac.FLAC__stream_decoder_set_metadata_ignore_all(decoder)

    libflac.FLAC__stream_decoder_get_state.restype = FLAC__StreamDecoderState
    libflac.FLAC__stream_decoder_get_state.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_state(decoder):
        return libflac.FLAC__stream_decoder_get_state(decoder)

    libflac.FLAC__stream_decoder_get_resolved_state_string.restype = c_char_p
    libflac.FLAC__stream_decoder_get_resolved_state_string.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_resolved_state_string(decoder):
        return libflac.FLAC__stream_decoder_get_resolved_state_string(decoder)

    libflac.FLAC__stream_decoder_get_md5_checking.restype = FLAC__bool
    libflac.FLAC__stream_decoder_get_md5_checking.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_md5_checking(decoder):
        return libflac.FLAC__stream_decoder_get_md5_checking(decoder)

    libflac.FLAC__stream_decoder_get_total_samples.restype = FLAC__uint64
    libflac.FLAC__stream_decoder_get_total_samples.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_total_samples(decoder):
        return libflac.FLAC__stream_decoder_get_total_samples(decoder)

    libflac.FLAC__stream_decoder_get_channels.restype = c_uint
    libflac.FLAC__stream_decoder_get_channels.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_channels(decoder):
        return libflac.FLAC__stream_decoder_get_channels(decoder)

    libflac.FLAC__stream_decoder_get_channel_assignment.restype = FLAC__ChannelAssignment
    libflac.FLAC__stream_decoder_get_channel_assignment.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_channel_assignment(decoder):
        return libflac.FLAC__stream_decoder_get_channel_assignment(decoder)

    libflac.FLAC__stream_decoder_get_bits_per_sample.restype = c_uint
    libflac.FLAC__stream_decoder_get_bits_per_sample.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_bits_per_sample(decoder):
        return libflac.FLAC__stream_decoder_get_bits_per_sample(decoder)

    libflac.FLAC__stream_decoder_get_sample_rate.restype = c_uint
    libflac.FLAC__stream_decoder_get_sample_rate.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_sample_rate(decoder):
        return libflac.FLAC__stream_decoder_get_sample_rate(decoder)

    libflac.FLAC__stream_decoder_get_blocksize.restype = c_uint
    libflac.FLAC__stream_decoder_get_blocksize.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_get_blocksize(decoder):
        return libflac.FLAC__stream_decoder_get_blocksize(decoder)

    libflac.FLAC__stream_decoder_get_decode_position.restype = FLAC__bool
    libflac.FLAC__stream_decoder_get_decode_position.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__uint64_p]

    def FLAC__stream_decoder_get_decode_position(decoder, position):
        return libflac.FLAC__stream_decoder_get_decode_position(decoder, position)

    libflac.FLAC__stream_decoder_init_stream.restype = FLAC__StreamDecoderInitStatus
    libflac.FLAC__stream_decoder_init_stream.argtypes = [POINTER(FLAC__StreamDecoder),
                                                         FLAC__StreamDecoderReadCallback,
                                                         FLAC__StreamDecoderSeekCallback,
                                                         FLAC__StreamDecoderTellCallback,
                                                         FLAC__StreamDecoderLengthCallback,
                                                         FLAC__StreamDecoderEofCallback,
                                                         FLAC__StreamDecoderWriteCallback,
                                                         FLAC__StreamDecoderMetadataCallback,
                                                         FLAC__StreamDecoderErrorCallback,
                                                         c_void_p]

    def FLAC__stream_decoder_init_stream(decoder, read_callback, seek_callback, tell_callback, length_callback, eof_callback, write_callback, metadata_callback, error_callback, client_data):
        return libflac.FLAC__stream_decoder_init_stream(decoder, read_callback, seek_callback, tell_callback, length_callback, eof_callback, write_callback, metadata_callback, error_callback, client_data)


    libflac.FLAC__stream_decoder_init_ogg_stream.restype = FLAC__StreamDecoderInitStatus
    libflac.FLAC__stream_decoder_init_ogg_stream.argtypes = [POINTER(FLAC__StreamDecoder),
                                                         FLAC__StreamDecoderReadCallback,
                                                         FLAC__StreamDecoderSeekCallback,
                                                         FLAC__StreamDecoderTellCallback,
                                                         FLAC__StreamDecoderLengthCallback,
                                                         FLAC__StreamDecoderEofCallback,
                                                         FLAC__StreamDecoderWriteCallback,
                                                         FLAC__StreamDecoderMetadataCallback,
                                                         FLAC__StreamDecoderErrorCallback,
                                                         c_void_p]

    def FLAC__stream_decoder_init_ogg_stream(decoder, read_callback, seek_callback, tell_callback, length_callback, eof_callback, write_callback, metadata_callback, error_callback, client_data):
        return libflac.FLAC__stream_decoder_init_ogg_stream(decoder, read_callback, seek_callback, tell_callback, length_callback, eof_callback, write_callback, metadata_callback, error_callback, client_data)

    libflac.FLAC__stream_decoder_init_file.restype = FLAC__StreamDecoderInitStatus
    libflac.FLAC__stream_decoder_init_file.argtypes = [POINTER(FLAC__StreamDecoder),
                                                         c_char_p,
                                                         FLAC__StreamDecoderWriteCallback,
                                                         FLAC__StreamDecoderMetadataCallback,
                                                         FLAC__StreamDecoderErrorCallback,
                                                         c_void_p]

    def FLAC__stream_decoder_init_file(decoder, filename, write_callback, metadata_callback, error_callback, client_data):
        return libflac.FLAC__stream_decoder_init_file(decoder, filename, write_callback, metadata_callback, error_callback, client_data)

    libflac.FLAC__stream_decoder_init_ogg_file.restype = FLAC__StreamDecoderInitStatus
    libflac.FLAC__stream_decoder_init_ogg_file.argtypes = [POINTER(FLAC__StreamDecoder),
                                                         c_char_p,
                                                         FLAC__StreamDecoderWriteCallback,
                                                         FLAC__StreamDecoderMetadataCallback,
                                                         FLAC__StreamDecoderErrorCallback,
                                                         c_void_p]

    def FLAC__stream_decoder_init_ogg_file(decoder, filename, write_callback, metadata_callback, error_callback, client_data):
        return libflac.FLAC__stream_decoder_init_ogg_file(decoder, filename, write_callback, metadata_callback, error_callback, client_data)

    libflac.FLAC__stream_decoder_finish.restype = FLAC__bool
    libflac.FLAC__stream_decoder_finish.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_finish(decoder):
        return libflac.FLAC__stream_decoder_finish(decoder)

    libflac.FLAC__stream_decoder_flush.restype = FLAC__bool
    libflac.FLAC__stream_decoder_flush.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_flush(decoder):
        return libflac.FLAC__stream_decoder_flush(decoder)

    libflac.FLAC__stream_decoder_reset.restype = FLAC__bool
    libflac.FLAC__stream_decoder_reset.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_reset(decoder):
        return libflac.FLAC__stream_decoder_reset(decoder)

    libflac.FLAC__stream_decoder_process_single.restype = FLAC__bool
    libflac.FLAC__stream_decoder_process_single.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_process_single(decoder):
        return libflac.FLAC__stream_decoder_process_single(decoder)

    libflac.FLAC__stream_decoder_process_until_end_of_metadata.restype = FLAC__bool
    libflac.FLAC__stream_decoder_process_until_end_of_metadata.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_process_until_end_of_metadata(decoder):
        return libflac.FLAC__stream_decoder_process_until_end_of_metadata(decoder)

    libflac.FLAC__stream_decoder_process_until_end_of_stream.restype = FLAC__bool
    libflac.FLAC__stream_decoder_process_until_end_of_stream.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_process_until_end_of_stream(decoder):
        return libflac.FLAC__stream_decoder_process_until_end_of_stream(decoder)

    libflac.FLAC__stream_decoder_skip_single_frame.restype = FLAC__bool
    libflac.FLAC__stream_decoder_skip_single_frame.argtypes = [POINTER(FLAC__StreamDecoder)]

    def FLAC__stream_decoder_skip_single_frame(decoder):
        return libflac.FLAC__stream_decoder_skip_single_frame(decoder)

    libflac.FLAC__stream_decoder_seek_absolute.restype = FLAC__bool
    libflac.FLAC__stream_decoder_seek_absolute.argtypes = [POINTER(FLAC__StreamDecoder), FLAC__uint64]

    def FLAC__stream_decoder_seek_absolute(decoder, sample):
        return libflac.FLAC__stream_decoder_seek_absolute(decoder, sample)

    # /stream_decoder

    # stream_encoder

    FLAC__StreamEncoderState = c_int

    libflac.FLAC__StreamEncoderStateString.restype = c_char_p
    libflac.FLAC__StreamEncoderStateString.argtypes = []

    def FLAC__StreamEncoderStateString():
        return libflac.FLAC__StreamEncoderStateString()


    FLAC__StreamEncoderInitStatus = c_int

    libflac.FLAC__StreamEncoderInitStatusString.restype = c_char_p
    libflac.FLAC__StreamEncoderInitStatusString.argtypes = []

    def FLAC__StreamEncoderInitStatusString():
        return libflac.FLAC__StreamEncoderInitStatusString()


    FLAC__StreamEncoderReadStatus = c_int

    libflac.FLAC__StreamEncoderReadStatusString.restype = c_char_p
    libflac.FLAC__StreamEncoderReadStatusString.argtypes = []

    def FLAC__StreamEncoderReadStatusString():
        return libflac.FLAC__StreamEncoderReadStatusString()


    FLAC__StreamEncoderWriteStatus = c_int

    libflac.FLAC__StreamEncoderWriteStatusString.restype = c_char_p
    libflac.FLAC__StreamEncoderWriteStatusString.argtypes = []

    def FLAC__StreamEncoderWriteStatusString():
        return libflac.FLAC__StreamEncoderWriteStatusString()


    FLAC__StreamEncoderSeekStatus = c_int

    libflac.FLAC__StreamEncoderSeekStatusString.restype = c_char_p
    libflac.FLAC__StreamEncoderSeekStatusString.argtypes = []

    def FLAC__StreamEncoderSeekStatusString():
        return libflac.FLAC__StreamEncoderSeekStatusString()


    FLAC__StreamEncoderTellStatus = c_int

    libflac.FLAC__StreamEncoderTellStatusString.restype = c_char_p
    libflac.FLAC__StreamEncoderTellStatusString.argtypes = []

    def FLAC__StreamEncoderTellStatusString():
        return libflac.FLAC__StreamEncoderTellStatusString()


    class FLAC__StreamEncoderProtected(Structure):
        _fields_ = [("dummy", c_int)]

    class FLAC__StreamEncoderPrivate(Structure):
        _fields_ = [("dummy", c_int)]

    class FLAC__StreamEncoder(Structure):
        _fields_ = [("protected_", POINTER(FLAC__StreamEncoderProtected)),
                    ("private_", POINTER(FLAC__StreamEncoderPrivate))]

    FLAC__StreamEncoderReadCallback = CFUNCTYPE(FLAC__StreamEncoderReadStatus, POINTER(FLAC__StreamEncoder), POINTER(FLAC__byte*0), c_size_t_p, c_void_p)

    FLAC__StreamEncoderWriteCallback = CFUNCTYPE(FLAC__StreamEncoderWriteStatus, POINTER(FLAC__StreamEncoder), POINTER(FLAC__byte*0), c_size_t, c_uint, c_uint, c_void_p)

    FLAC__StreamEncoderSeekCallback = CFUNCTYPE(FLAC__StreamEncoderSeekStatus, POINTER(FLAC__StreamEncoder), FLAC__uint64,  c_void_p)

    FLAC__StreamEncoderTellCallback = CFUNCTYPE(FLAC__StreamEncoderTellStatus, POINTER(FLAC__StreamEncoder), FLAC__uint64_p,  c_void_p)

    FLAC__StreamEncoderMetadataCallback = CFUNCTYPE(None, POINTER(FLAC__StreamEncoder), POINTER(FLAC__StreamMetadata),  c_void_p)

    FLAC__StreamEncoderProgressCallback = CFUNCTYPE(None, POINTER(FLAC__StreamEncoder), FLAC__uint64,FLAC__uint64, c_uint, c_uint,  c_void_p)


    libflac.FLAC__stream_encoder_new.restype = POINTER(FLAC__StreamEncoder)
    libflac.FLAC__stream_encoder_new.argtypes = []

    def FLAC__stream_encoder_new():
        return libflac.FLAC__stream_encoder_new()

    libflac.FLAC__stream_encoder_delete.restype = None
    libflac.FLAC__stream_encoder_delete.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_delete(encoder):
        return libflac.FLAC__stream_encoder_delete(encoder)


    libflac.FLAC__stream_encoder_set_ogg_serial_number.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_ogg_serial_number.argtypes = [POINTER(FLAC__StreamEncoder), c_long]

    def FLAC__stream_encoder_set_ogg_serial_number(encoder, serial_number):
        return libflac.FLAC__stream_encoder_set_ogg_serial_number(encoder, serial_number)

    libflac.FLAC__stream_encoder_set_verify.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_verify.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_verify(encoder, value):
        return libflac.FLAC__stream_encoder_set_verify(encoder, value)

    libflac.FLAC__stream_encoder_set_streamable_subset.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_streamable_subset.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_streamable_subset(encoder, value):
        return libflac.FLAC__stream_encoder_set_streamable_subset(encoder, value)

    libflac.FLAC__stream_encoder_set_channels.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_channels.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_channels(encoder, value):
        return libflac.FLAC__stream_encoder_set_channels(encoder, value)

    libflac.FLAC__stream_encoder_set_bits_per_sample.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_bits_per_sample.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_bits_per_sample(encoder, value):
        return libflac.FLAC__stream_encoder_set_bits_per_sample(encoder, value)

    libflac.FLAC__stream_encoder_set_sample_rate.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_sample_rate.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_sample_rate(encoder, value):
        return libflac.FLAC__stream_encoder_set_sample_rate(encoder, value)

    libflac.FLAC__stream_encoder_set_compression_level.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_compression_level.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_compression_level(encoder, value):
        return libflac.FLAC__stream_encoder_set_compression_level(encoder, value)

    libflac.FLAC__stream_encoder_set_blocksize.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_blocksize.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_blocksize(encoder, value):
        return libflac.FLAC__stream_encoder_set_blocksize(encoder, value)

    libflac.FLAC__stream_encoder_set_do_mid_side_stereo.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_do_mid_side_stereo.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_do_mid_side_stereo(encoder, value):
        return libflac.FLAC__stream_encoder_set_do_mid_side_stereo(encoder, value)

    libflac.FLAC__stream_encoder_set_loose_mid_side_stereo.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_loose_mid_side_stereo.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_loose_mid_side_stereo(encoder, value):
        return libflac.FLAC__stream_encoder_set_loose_mid_side_stereo(encoder, value)

    libflac.FLAC__stream_encoder_set_apodization.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_apodization.argtypes = [POINTER(FLAC__StreamEncoder), c_char_p]

    def FLAC__stream_encoder_set_apodization(encoder, specification):
        return libflac.FLAC__stream_encoder_set_apodization(encoder, specification)

    libflac.FLAC__stream_encoder_set_max_lpc_order.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_max_lpc_order.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_max_lpc_order(encoder, value):
        return libflac.FLAC__stream_encoder_set_max_lpc_order(encoder, value)

    libflac.FLAC__stream_encoder_set_qlp_coeff_precision.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_qlp_coeff_precision.argtypes = [POINTER(FLAC__StreamEncoder), c_uint]

    def FLAC__stream_encoder_set_qlp_coeff_precision(encoder, value):
        return libflac.FLAC__stream_encoder_set_qlp_coeff_precision(encoder, value)

    libflac.FLAC__stream_encoder_set_do_qlp_coeff_prec_search.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_do_qlp_coeff_prec_search.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_do_qlp_coeff_prec_search(encoder, value):
        return libflac.FLAC__stream_encoder_set_do_qlp_coeff_prec_search(encoder, value)

    libflac.FLAC__stream_encoder_set_do_escape_coding.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_do_escape_coding.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_do_escape_coding(encoder, value):
        return libflac.FLAC__stream_encoder_set_do_escape_coding(encoder, value)

    libflac.FLAC__stream_encoder_set_do_exhaustive_model_search.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_do_exhaustive_model_search.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_do_exhaustive_model_search(encoder, value):
        return libflac.FLAC__stream_encoder_set_do_exhaustive_model_search(encoder, value)

    libflac.FLAC__stream_encoder_set_min_residual_partition_order.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_min_residual_partition_order.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_min_residual_partition_order(encoder, value):
        return libflac.FLAC__stream_encoder_set_min_residual_partition_order(encoder, value)

    libflac.FLAC__stream_encoder_set_max_residual_partition_order.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_max_residual_partition_order.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_max_residual_partition_order(encoder, value):
        return libflac.FLAC__stream_encoder_set_max_residual_partition_order(encoder, value)

    libflac.FLAC__stream_encoder_set_rice_parameter_search_dist.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_rice_parameter_search_dist.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__bool]

    def FLAC__stream_encoder_set_rice_parameter_search_dist(encoder, value):
        return libflac.FLAC__stream_encoder_set_rice_parameter_search_dist(encoder, value)

    libflac.FLAC__stream_encoder_set_total_samples_estimate.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_total_samples_estimate.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__uint64]

    def FLAC__stream_encoder_set_total_samples_estimate(encoder, value):
        return libflac.FLAC__stream_encoder_set_total_samples_estimate(encoder, value)

    libflac.FLAC__stream_encoder_set_metadata.restype = FLAC__bool
    libflac.FLAC__stream_encoder_set_metadata.argtypes = [POINTER(FLAC__StreamEncoder), POINTER(POINTER(FLAC__StreamMetadata)), c_uint]

    def FLAC__stream_encoder_set_metadata(encoder, metadata, num_blocks):
        return libflac.FLAC__stream_encoder_set_metadata(encoder, metadata, num_blocks)

    libflac.FLAC__stream_encoder_get_state.restype = FLAC__StreamEncoderState
    libflac.FLAC__stream_encoder_get_state.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_state(encoder):
        return libflac.FLAC__stream_encoder_get_state(encoder)

    libflac.FLAC__stream_encoder_get_verify_decoder_state.restype = FLAC__StreamEncoderState
    libflac.FLAC__stream_encoder_get_verify_decoder_state.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_verify_decoder_state(encoder):
        return libflac.FLAC__stream_encoder_get_verify_decoder_state(encoder)

    libflac.FLAC__stream_encoder_get_resolved_state_string.restype = c_char_p
    libflac.FLAC__stream_encoder_get_resolved_state_string.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_resolved_state_string(encoder):
        return libflac.FLAC__stream_encoder_get_resolved_state_string(encoder)

    libflac.FLAC__stream_encoder_get_verify_decoder_error_stats.restype = None
    libflac.FLAC__stream_encoder_get_verify_decoder_error_stats.argtypes = [POINTER(FLAC__StreamEncoder), FLAC__uint64_p, c_uint_p, c_uint_p, c_uint_p, FLAC__int32_p, FLAC__int32_p]

    def FLAC__stream_encoder_get_verify_decoder_error_stats(encoder, absolute_sample, frame_number, channel, sample, expected, got):
        return libflac.FLAC__stream_encoder_get_verify_decoder_error_stats(encoder, absolute_sample, frame_number, channel, sample, expected, got)

    libflac.FLAC__stream_encoder_get_verify.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_verify.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_verify(encoder):
        return libflac.FLAC__stream_encoder_get_verify(encoder)

    libflac.FLAC__stream_encoder_get_streamable_subset.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_streamable_subset.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_streamable_subset(encoder):
        return libflac.FLAC__stream_encoder_get_streamable_subset(encoder)

    libflac.FLAC__stream_encoder_get_channels.restype = c_uint
    libflac.FLAC__stream_encoder_get_channels.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_channels(encoder):
        return libflac.FLAC__stream_encoder_get_channels(encoder)

    libflac.FLAC__stream_encoder_get_bits_per_sample.restype = c_uint
    libflac.FLAC__stream_encoder_get_bits_per_sample.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_bits_per_sample(encoder):
        return libflac.FLAC__stream_encoder_get_bits_per_sample(encoder)

    libflac.FLAC__stream_encoder_get_sample_rate.restype = c_uint
    libflac.FLAC__stream_encoder_get_sample_rate.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_sample_rate(encoder):
        return libflac.FLAC__stream_encoder_get_sample_rate(encoder)

    libflac.FLAC__stream_encoder_get_blocksize.restype = c_uint
    libflac.FLAC__stream_encoder_get_blocksize.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_blocksize(encoder):
        return libflac.FLAC__stream_encoder_get_blocksize(encoder)

    libflac.FLAC__stream_encoder_get_do_mid_side_stereo.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_do_mid_side_stereo.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_do_mid_side_stereo(encoder):
        return libflac.FLAC__stream_encoder_get_do_mid_side_stereo(encoder)

    libflac.FLAC__stream_encoder_get_loose_mid_side_stereo.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_loose_mid_side_stereo.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_loose_mid_side_stereo(encoder):
        return libflac.FLAC__stream_encoder_get_loose_mid_side_stereo(encoder)

    libflac.FLAC__stream_encoder_get_max_lpc_order.restype = c_uint
    libflac.FLAC__stream_encoder_get_max_lpc_order.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_max_lpc_order(encoder):
        return libflac.FLAC__stream_encoder_get_max_lpc_order(encoder)

    libflac.FLAC__stream_encoder_get_qlp_coeff_precision.restype = c_uint
    libflac.FLAC__stream_encoder_get_qlp_coeff_precision.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_qlp_coeff_precision(encoder):
        return libflac.FLAC__stream_encoder_get_qlp_coeff_precision(encoder)

    libflac.FLAC__stream_encoder_get_do_qlp_coeff_prec_search.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_do_qlp_coeff_prec_search.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_do_qlp_coeff_prec_search(encoder):
        return libflac.FLAC__stream_encoder_get_do_qlp_coeff_prec_search(encoder)

    libflac.FLAC__stream_encoder_get_do_escape_coding.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_do_escape_coding.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_do_escape_coding(encoder):
        return libflac.FLAC__stream_encoder_get_do_escape_coding(encoder)

    libflac.FLAC__stream_encoder_get_do_exhaustive_model_search.restype = FLAC__bool
    libflac.FLAC__stream_encoder_get_do_exhaustive_model_search.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_do_exhaustive_model_search(encoder):
        return libflac.FLAC__stream_encoder_get_do_exhaustive_model_search(encoder)

    libflac.FLAC__stream_encoder_get_min_residual_partition_order.restype = c_uint
    libflac.FLAC__stream_encoder_get_min_residual_partition_order.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_min_residual_partition_order(encoder):
        return libflac.FLAC__stream_encoder_get_min_residual_partition_order(encoder)

    libflac.FLAC__stream_encoder_get_max_residual_partition_order.restype = c_uint
    libflac.FLAC__stream_encoder_get_max_residual_partition_order.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_max_residual_partition_order(encoder):
        return libflac.FLAC__stream_encoder_get_max_residual_partition_order(encoder)

    libflac.FLAC__stream_encoder_get_rice_parameter_search_dist.restype = c_uint
    libflac.FLAC__stream_encoder_get_rice_parameter_search_dist.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_rice_parameter_search_dist(encoder):
        return libflac.FLAC__stream_encoder_get_rice_parameter_search_dist(encoder)

    libflac.FLAC__stream_encoder_get_total_samples_estimate.restype = FLAC__uint64
    libflac.FLAC__stream_encoder_get_total_samples_estimate.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_get_total_samples_estimate(encoder):
        return libflac.FLAC__stream_encoder_get_total_samples_estimate(encoder)

    libflac.FLAC__stream_encoder_init_stream.restype = FLAC__StreamEncoderInitStatus
    libflac.FLAC__stream_encoder_init_stream.argtypes = [POINTER(FLAC__StreamEncoder),
                                                         FLAC__StreamEncoderWriteCallback,
                                                         FLAC__StreamEncoderSeekCallback,
                                                         FLAC__StreamEncoderTellCallback,
                                                         FLAC__StreamEncoderMetadataCallback,
                                                         c_void_p]

    def FLAC__stream_encoder_init_stream(encoder, write_callback, seek_callback, tell_callback, metadata_callback,client_data):
        return libflac.FLAC__stream_encoder_init_stream(encoder, write_callback, seek_callback, tell_callback, metadata_callback,client_data)

    libflac.FLAC__stream_encoder_init_ogg_stream.restype = FLAC__StreamEncoderInitStatus
    libflac.FLAC__stream_encoder_init_ogg_stream.argtypes = [POINTER(FLAC__StreamEncoder),
                                                         FLAC__StreamEncoderReadCallback,
                                                         FLAC__StreamEncoderWriteCallback,
                                                         FLAC__StreamEncoderSeekCallback,
                                                         FLAC__StreamEncoderTellCallback,
                                                         FLAC__StreamEncoderMetadataCallback,
                                                         c_void_p]

    def FLAC__stream_encoder_init_ogg_stream(encoder, read_callback, write_callback, seek_callback, tell_callback, metadata_callback,client_data):
        return libflac.FLAC__stream_encoder_init_ogg_stream(encoder, read_callback, write_callback, seek_callback, tell_callback, metadata_callback,client_data)

    libflac.FLAC__stream_encoder_init_file.restype = FLAC__StreamEncoderInitStatus
    libflac.FLAC__stream_encoder_init_file.argtypes = [POINTER(FLAC__StreamEncoder),
                                                         c_char_p,
                                                         FLAC__StreamEncoderProgressCallback,
                                                         c_void_p]

    def FLAC__stream_encoder_init_file(encoder, filename, progress_callback,client_data):
        return libflac.FLAC__stream_encoder_init_file(encoder, filename, progress_callback,client_data)


    libflac.FLAC__stream_encoder_init_ogg_file.restype = FLAC__StreamEncoderInitStatus
    libflac.FLAC__stream_encoder_init_ogg_file.argtypes = [POINTER(FLAC__StreamEncoder),
                                                         c_char_p,
                                                         FLAC__StreamEncoderProgressCallback,
                                                         c_void_p]

    def FLAC__stream_encoder_init_ogg_file(encoder, filename, progress_callback,client_data):
        return libflac.FLAC__stream_encoder_init_ogg_file(encoder, filename, progress_callback,client_data)

    libflac.FLAC__stream_encoder_finish.restype = FLAC__bool
    libflac.FLAC__stream_encoder_finish.argtypes = [POINTER(FLAC__StreamEncoder)]

    def FLAC__stream_encoder_finish(encoder):
        return libflac.FLAC__stream_encoder_finish(encoder)

    libflac.FLAC__stream_encoder_process.restype = FLAC__bool
    libflac.FLAC__stream_encoder_process.argtypes = [POINTER(FLAC__StreamEncoder), POINTER(FLAC__int32_p*0), c_uint]

    def FLAC__stream_encoder_process(encoder, buffer, samples):
        return libflac.FLAC__stream_encoder_process(encoder, buffer, samples)

    libflac.FLAC__stream_encoder_process_interleaved.restype = FLAC__bool
    libflac.FLAC__stream_encoder_process_interleaved.argtypes = [POINTER(FLAC__StreamEncoder), POINTER(FLAC__int32*0), c_uint]

    def FLAC__stream_encoder_process_interleaved(encoder, buffer, samples):
        return libflac.FLAC__stream_encoder_process_interleaved(encoder, buffer, samples)

    # /stream_encoder
