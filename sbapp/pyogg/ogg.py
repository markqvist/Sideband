############################################################
# Ogg license:                                             #
############################################################
"""
Copyright (c) 2002, Xiph.org Foundation

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
from ctypes import c_int, c_int8, c_int16, c_int32, c_int64, c_uint, c_uint8, c_uint16, c_uint32, c_uint64, c_float, c_long, c_ulong, c_char, c_char_p, c_ubyte, c_longlong, c_ulonglong, c_size_t, c_void_p, c_double, POINTER, pointer, cast
import ctypes.util
import sys
from traceback import print_exc as _print_exc
import os

from .library_loader import Library, ExternalLibrary, ExternalLibraryError


def get_raw_libname(name):
    name = os.path.splitext(name)[0].lower()
    for x in "0123456789._- ":name=name.replace(x,"")
    return name

# Define a function to convert strings to char-pointers.  In Python 3
# all strings are Unicode, while in Python 2 they were ASCII-encoded.
# FIXME: Does PyOgg even support Python 2?
if sys.version_info.major > 2:
    to_char_p = lambda s: s.encode('utf-8')
else:
    to_char_p = lambda s: s

__here = os.getcwd()

libogg = None

try:
    names = {
        "Windows": "ogg.dll",
        "Darwin": "libogg.0.dylib",
        "external": "ogg"
    }
    libogg = Library.load(names, tests = [lambda lib: hasattr(lib, "oggpack_writeinit")])
except ExternalLibraryError:
    pass
except:
    _print_exc()

if libogg is not None:
    PYOGG_OGG_AVAIL = True
else:
    PYOGG_OGG_AVAIL = False

if PYOGG_OGG_AVAIL:
    # Sanity check also satisfies mypy type checking
    assert libogg is not None

    # ctypes
    c_ubyte_p = POINTER(c_ubyte)
    c_uchar = c_ubyte
    c_uchar_p = c_ubyte_p
    c_float_p = POINTER(c_float)
    c_float_p_p = POINTER(c_float_p)
    c_float_p_p_p = POINTER(c_float_p_p)
    c_char_p_p = POINTER(c_char_p)
    c_int_p = POINTER(c_int)
    c_long_p = POINTER(c_long)

    # os_types
    ogg_int16_t = c_int16
    ogg_uint16_t = c_uint16
    ogg_int32_t = c_int32
    ogg_uint32_t = c_uint32
    ogg_int64_t = c_int64
    ogg_uint64_t = c_uint64
    ogg_int64_t_p = POINTER(ogg_int64_t)

    # ogg
    class ogg_iovec_t(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ogg_iovec_t;
        """
        _fields_ = [("iov_base", c_void_p),
                    ("iov_len", c_size_t)]

    class oggpack_buffer(ctypes.Structure):
        """
        Wrapper for:
            typedef struct oggpack_buffer;
        """
        _fields_ = [("endbyte", c_long),
                    ("endbit", c_int),
                    ("buffer", c_uchar_p),
                    ("ptr", c_uchar_p),
                    ("storage", c_long)]

    class ogg_page(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ogg_page;
        """
        _fields_ = [("header", c_uchar_p),
                    ("header_len", c_long),
                    ("body", c_uchar_p),
                    ("body_len", c_long)]

    class ogg_stream_state(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ogg_stream_state;
        """
        _fields_ = [("body_data", c_uchar_p),
                    ("body_storage", c_long),
                    ("body_fill", c_long),
                    ("body_returned", c_long),

                    ("lacing_vals", c_int),
                    ("granule_vals", ogg_int64_t),

                    ("lacing_storage", c_long),
                    ("lacing_fill", c_long),
                    ("lacing_packet", c_long),
                    ("lacing_returned", c_long),

                    ("header", c_uchar*282),
                    ("header_fill", c_int),

                    ("e_o_s", c_int),
                    ("b_o_s", c_int),

                    ("serialno", c_long),
                    ("pageno", c_long),
                    ("packetno", ogg_int64_t),
                    ("granulepos", ogg_int64_t)]

    class ogg_packet(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ogg_packet;
        """
        _fields_ = [("packet", c_uchar_p),
                    ("bytes", c_long),
                    ("b_o_s", c_long),
                    ("e_o_s", c_long),

                    ("granulepos", ogg_int64_t),

                    ("packetno", ogg_int64_t)]

        def __str__(self):
            bos = ""
            if self.b_o_s:
                bos = "beginning of stream, "
            eos = ""
            if self.e_o_s:
                eos = "end of stream, "

            # Converting the data will cause a seg-fault if the memory isn't valid
            data = bytes(self.packet[0:self.bytes])
            value = (
                f"Ogg Packet <{hex(id(self))}>: " +
                f"number {self.packetno}, " +
                f"granule position {self.granulepos}, " +
                bos + eos +
                f"{self.bytes} bytes"
            )
            return value

    class ogg_sync_state(ctypes.Structure):
        """
        Wrapper for:
            typedef struct ogg_sync_state;
        """
        _fields_ = [("data", c_uchar_p),
                    ("storage", c_int),
                    ("fill", c_int),
                    ("returned", c_int),

                    ("unsynched", c_int),
                    ("headerbytes", c_int),
                    ("bodybytes", c_int)]

    b_p = POINTER(oggpack_buffer)
    oy_p = POINTER(ogg_sync_state)
    op_p = POINTER(ogg_packet)
    og_p = POINTER(ogg_page)
    os_p = POINTER(ogg_stream_state)
    iov_p = POINTER(ogg_iovec_t)
        
    libogg.oggpack_writeinit.restype = None
    libogg.oggpack_writeinit.argtypes = [b_p]

    def oggpack_writeinit(b):
        libogg.oggpack_writeinit(b)

    try:
        libogg.oggpack_writecheck.restype = c_int
        libogg.oggpack_writecheck.argtypes = [b_p]
        def oggpack_writecheck(b):
            libogg.oggpack_writecheck(b)
    except:
        pass

    libogg.oggpack_writetrunc.restype = None
    libogg.oggpack_writetrunc.argtypes = [b_p, c_long]

    def oggpack_writetrunc(b, bits):
        libogg.oggpack_writetrunc(b, bits)

    libogg.oggpack_writealign.restype = None
    libogg.oggpack_writealign.argtypes = [b_p]

    def oggpack_writealign(b):
        libogg.oggpack_writealign(b)

    libogg.oggpack_writecopy.restype = None
    libogg.oggpack_writecopy.argtypes = [b_p, c_void_p, c_long]

    def oggpack_writecopy(b, source, bits):
        libogg.oggpack_writecopy(b, source, bits)

    libogg.oggpack_reset.restype = None
    libogg.oggpack_reset.argtypes = [b_p]

    def oggpack_reset(b):
        libogg.oggpack_reset(b)

    libogg.oggpack_writeclear.restype = None
    libogg.oggpack_writeclear.argtypes = [b_p]

    def oggpack_writeclear(b):
        libogg.oggpack_writeclear(b)

    libogg.oggpack_readinit.restype = None
    libogg.oggpack_readinit.argtypes = [b_p, c_uchar_p, c_int]

    def oggpack_readinit(b, buf, bytes):
        libogg.oggpack_readinit(b, buf, bytes)

    libogg.oggpack_write.restype = None
    libogg.oggpack_write.argtypes = [b_p, c_ulong, c_int]

    def oggpack_write(b, value, bits):
        libogg.oggpack_write(b, value, bits)

    libogg.oggpack_look.restype = c_long
    libogg.oggpack_look.argtypes = [b_p, c_int]

    def oggpack_look(b, bits):
        return libogg.oggpack_look(b, bits)

    libogg.oggpack_look1.restype = c_long
    libogg.oggpack_look1.argtypes = [b_p]

    def oggpack_look1(b):
        return libogg.oggpack_look1(b)

    libogg.oggpack_adv.restype = None
    libogg.oggpack_adv.argtypes = [b_p, c_int]

    def oggpack_adv(b, bits):
        libogg.oggpack_adv(b, bits)

    libogg.oggpack_adv1.restype = None
    libogg.oggpack_adv1.argtypes = [b_p]

    def oggpack_adv1(b):
        libogg.oggpack_adv1(b)

    libogg.oggpack_read.restype = c_long
    libogg.oggpack_read.argtypes = [b_p, c_int]

    def oggpack_read(b, bits):
        return libogg.oggpack_read(b, bits)

    libogg.oggpack_read1.restype = c_long
    libogg.oggpack_read1.argtypes = [b_p]

    def oggpack_read1(b):
        return libogg.oggpack_read1(b)

    libogg.oggpack_bytes.restype = c_long
    libogg.oggpack_bytes.argtypes = [b_p]

    def oggpack_bytes(b):
        return libogg.oggpack_bytes(b)

    libogg.oggpack_bits.restype = c_long
    libogg.oggpack_bits.argtypes = [b_p]

    def oggpack_bits(b):
        return libogg.oggpack_bits(b)

    libogg.oggpack_get_buffer.restype = c_uchar_p
    libogg.oggpack_get_buffer.argtypes = [b_p]

    def oggpack_get_buffer(b):
        return libogg.oggpack_get_buffer(b)



    libogg.oggpackB_writeinit.restype = None
    libogg.oggpackB_writeinit.argtypes = [b_p]

    def oggpackB_writeinit(b):
        libogg.oggpackB_writeinit(b)
    
    try:
        libogg.oggpackB_writecheck.restype = c_int
        libogg.oggpackB_writecheck.argtypes = [b_p]

        def oggpackB_writecheck(b):
            return libogg.oggpackB_writecheck(b) 
    except:
        pass

    libogg.oggpackB_writetrunc.restype = None
    libogg.oggpackB_writetrunc.argtypes = [b_p, c_long]

    def oggpackB_writetrunc(b, bits):
        libogg.oggpackB_writetrunc(b, bits)

    libogg.oggpackB_writealign.restype = None
    libogg.oggpackB_writealign.argtypes = [b_p]

    def oggpackB_writealign(b):
        libogg.oggpackB_writealign(b)

    libogg.oggpackB_writecopy.restype = None
    libogg.oggpackB_writecopy.argtypes = [b_p, c_void_p, c_long]

    def oggpackB_writecopy(b, source, bits):
        libogg.oggpackB_writecopy(b, source, bits)

    libogg.oggpackB_reset.restype = None
    libogg.oggpackB_reset.argtypes = [b_p]

    def oggpackB_reset(b):
        libogg.oggpackB_reset(b)

    libogg.oggpackB_reset.restype = None
    libogg.oggpackB_writeclear.argtypes = [b_p]

    def oggpackB_reset(b):
        libogg.oggpackB_reset(b)

    libogg.oggpackB_readinit.restype = None
    libogg.oggpackB_readinit.argtypes = [b_p, c_uchar_p, c_int]

    def oggpackB_readinit(b, buf, bytes):
        libogg.oggpackB_readinit(b, buf, bytes)

    libogg.oggpackB_write.restype = None
    libogg.oggpackB_write.argtypes = [b_p, c_ulong, c_int]

    def oggpackB_write(b, value, bits):
        libogg.oggpackB_write(b, value, bits)

    libogg.oggpackB_look.restype = c_long
    libogg.oggpackB_look.argtypes = [b_p, c_int]

    def oggpackB_look(b, bits):
        return libogg.oggpackB_look(b, bits)

    libogg.oggpackB_look1.restype = c_long
    libogg.oggpackB_look1.argtypes = [b_p]

    def oggpackB_look1(b):
        return libogg.oggpackB_look1(b)

    libogg.oggpackB_adv.restype = None
    libogg.oggpackB_adv.argtypes = [b_p, c_int]

    def oggpackB_adv(b, bits):
        libogg.oggpackB_adv(b, bits)

    libogg.oggpackB_adv1.restype = None
    libogg.oggpackB_adv1.argtypes = [b_p]

    def oggpackB_adv1(b):
        libogg.oggpackB_adv1(b)

    libogg.oggpackB_read.restype = c_long
    libogg.oggpackB_read.argtypes = [b_p, c_int]

    def oggpackB_read(b, bits):
        return libogg.oggpackB_read(b, bits)

    libogg.oggpackB_read1.restype = c_long
    libogg.oggpackB_read1.argtypes = [b_p]

    def oggpackB_read1(b):
        return libogg.oggpackB_read1(b)

    libogg.oggpackB_bytes.restype = c_long
    libogg.oggpackB_bytes.argtypes = [b_p]

    def oggpackB_bytes(b):
        return libogg.oggpackB_bytes(b)

    libogg.oggpackB_bits.restype = c_long
    libogg.oggpackB_bits.argtypes = [b_p]

    def oggpackB_bits(b):
        return libogg.oggpackB_bits(b)

    libogg.oggpackB_get_buffer.restype = c_uchar_p
    libogg.oggpackB_get_buffer.argtypes = [b_p]

    def oggpackB_get_buffer(b):
        return libogg.oggpackB_get_buffer(b)



    libogg.ogg_stream_packetin.restype = c_int
    libogg.ogg_stream_packetin.argtypes = [os_p, op_p]

    def ogg_stream_packetin(os, op):
        return libogg.ogg_stream_packetin(os, op)

    try:
        libogg.ogg_stream_iovecin.restype = c_int
        libogg.ogg_stream_iovecin.argtypes = [os_p, iov_p, c_int, c_long, ogg_int64_t]

        def ogg_stream_iovecin(os, iov, count, e_o_s, granulepos):
            return libogg.ogg_stream_iovecin(os, iov, count, e_o_s, granulepos)
    except:
        pass

    libogg.ogg_stream_pageout.restype = c_int
    libogg.ogg_stream_pageout.argtypes = [os_p, og_p]

    def ogg_stream_pageout(os, og):
        return libogg.ogg_stream_pageout(os, og)

    try:
        libogg.ogg_stream_pageout_fill.restype = c_int
        libogg.ogg_stream_pageout_fill.argtypes = [os_p, og_p, c_int]
        def ogg_stream_pageout_fill(os, og, nfill):
            return libogg.ogg_stream_pageout_fill(os, og, nfill)
    except:
        pass

    libogg.ogg_stream_flush.restype = c_int
    libogg.ogg_stream_flush.argtypes = [os_p, og_p]

    def ogg_stream_flush(os, og):
        return libogg.ogg_stream_flush(os, og)

    try:
        libogg.ogg_stream_flush_fill.restype = c_int
        libogg.ogg_stream_flush_fill.argtypes = [os_p, og_p, c_int]
        def ogg_stream_flush_fill(os, og, nfill):
            return libogg.ogg_stream_flush_fill(os, og, nfill)
    except:
        pass



    libogg.ogg_sync_init.restype = c_int
    libogg.ogg_sync_init.argtypes = [oy_p]

    def ogg_sync_init(oy):
        return libogg.ogg_sync_init(oy)

    libogg.ogg_sync_clear.restype = c_int
    libogg.ogg_sync_clear.argtypes = [oy_p]

    def ogg_sync_clear(oy):
        return libogg.ogg_sync_clear(oy)

    libogg.ogg_sync_reset.restype = c_int
    libogg.ogg_sync_reset.argtypes = [oy_p]

    def ogg_sync_reset(oy):
        return libogg.ogg_sync_reset(oy)

    libogg.ogg_sync_destroy.restype = c_int
    libogg.ogg_sync_destroy.argtypes = [oy_p]

    def ogg_sync_destroy(oy):
        return libogg.ogg_sync_destroy(oy)

    try:
        libogg.ogg_sync_check.restype = c_int
        libogg.ogg_sync_check.argtypes = [oy_p]
        def ogg_sync_check(oy):
            return libogg.ogg_sync_check(oy)
    except:
        pass



    libogg.ogg_sync_buffer.restype = c_char_p
    libogg.ogg_sync_buffer.argtypes = [oy_p, c_long]

    def ogg_sync_buffer(oy, size):
        return libogg.ogg_sync_buffer(oy, size)

    libogg.ogg_sync_wrote.restype = c_int
    libogg.ogg_sync_wrote.argtypes = [oy_p, c_long]

    def ogg_sync_wrote(oy, bytes):
        return libogg.ogg_sync_wrote(oy, bytes)

    libogg.ogg_sync_pageseek.restype = c_int
    libogg.ogg_sync_pageseek.argtypes = [oy_p, og_p]

    def ogg_sync_pageseek(oy, og):
        return libogg.ogg_sync_pageseek(oy, og)

    libogg.ogg_sync_pageout.restype = c_long
    libogg.ogg_sync_pageout.argtypes = [oy_p, og_p]

    def ogg_sync_pageout(oy, og):
        return libogg.ogg_sync_pageout(oy, og)

    libogg.ogg_stream_pagein.restype = c_int
    libogg.ogg_stream_pagein.argtypes = [os_p, og_p]

    def ogg_stream_pagein(os, og):
        return libogg.ogg_stream_pagein(oy, og)

    libogg.ogg_stream_packetout.restype = c_int
    libogg.ogg_stream_packetout.argtypes = [os_p, op_p]

    def ogg_stream_packetout(os, op):
        return libogg.ogg_stream_packetout(oy, op)

    libogg.ogg_stream_packetpeek.restype = c_int
    libogg.ogg_stream_packetpeek.argtypes = [os_p, op_p]

    def ogg_stream_packetpeek(os, op):
        return libogg.ogg_stream_packetpeek(os, op)



    libogg.ogg_stream_init.restype = c_int
    libogg.ogg_stream_init.argtypes = [os_p, c_int]

    def ogg_stream_init(os, serialno):
        return libogg.ogg_stream_init(os, serialno)

    libogg.ogg_stream_clear.restype = c_int
    libogg.ogg_stream_clear.argtypes = [os_p]

    def ogg_stream_clear(os):
        return libogg.ogg_stream_clear(os)

    libogg.ogg_stream_reset.restype = c_int
    libogg.ogg_stream_reset.argtypes = [os_p]

    def ogg_stream_reset(os):
        return libogg.ogg_stream_reset(os)

    libogg.ogg_stream_reset_serialno.restype = c_int
    libogg.ogg_stream_reset_serialno.argtypes = [os_p, c_int]

    def ogg_stream_reset_serialno(os, serialno):
        return libogg.ogg_stream_reset_serialno(os, serialno)

    libogg.ogg_stream_destroy.restype = c_int
    libogg.ogg_stream_destroy.argtypes = [os_p]

    def ogg_stream_destroy(os):
        return libogg.ogg_stream_destroy(os)

    try:
        libogg.ogg_stream_check.restype = c_int
        libogg.ogg_stream_check.argtypes = [os_p]
        def ogg_stream_check(os):
            return libogg.ogg_stream_check(os)
    except:
        pass

    libogg.ogg_stream_eos.restype = c_int
    libogg.ogg_stream_eos.argtypes = [os_p]

    def ogg_stream_eos(os):
        return libogg.ogg_stream_eos(os)



    libogg.ogg_page_checksum_set.restype = None
    libogg.ogg_page_checksum_set.argtypes = [og_p]

    def ogg_page_checksum_set(og):
        libogg.ogg_page_checksum_set(og)



    libogg.ogg_page_version.restype = c_int
    libogg.ogg_page_version.argtypes = [og_p]

    def ogg_page_version(og):
        return libogg.ogg_page_version(og)

    libogg.ogg_page_continued.restype = c_int
    libogg.ogg_page_continued.argtypes = [og_p]

    def ogg_page_continued(og):
        return libogg.ogg_page_continued(og)

    libogg.ogg_page_bos.restype = c_int
    libogg.ogg_page_bos.argtypes = [og_p]

    def ogg_page_bos(og):
        return libogg.ogg_page_bos(og)

    libogg.ogg_page_eos.restype = c_int
    libogg.ogg_page_eos.argtypes = [og_p]

    def ogg_page_eos(og):
        return libogg.ogg_page_eos(og)

    libogg.ogg_page_granulepos.restype = ogg_int64_t
    libogg.ogg_page_granulepos.argtypes = [og_p]

    def ogg_page_granulepos(og):
        return libogg.ogg_page_granulepos(og)

    libogg.ogg_page_serialno.restype = c_int
    libogg.ogg_page_serialno.argtypes = [og_p]

    def ogg_page_serialno(og):
        return libogg.ogg_page_serialno(og)

    libogg.ogg_page_pageno.restype = c_long
    libogg.ogg_page_pageno.argtypes = [og_p]

    def ogg_page_pageno(og):
        return libogg.ogg_page_pageno(og)

    libogg.ogg_page_packets.restype = c_int
    libogg.ogg_page_packets.argtypes = [og_p]

    def ogg_page_packets(og):
        return libogg.ogg_page_packets(og)



    libogg.ogg_packet_clear.restype = None
    libogg.ogg_packet_clear.argtypes = [op_p]

    def ogg_packet_clear(op):
        libogg.ogg_packet_clear(op)
