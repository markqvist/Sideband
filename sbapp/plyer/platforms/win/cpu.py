'''
Module of Windows API for plyer.cpu.
'''

from ctypes import (
    c_ulonglong, c_ulong, byref,
    Structure, POINTER, Union, windll, create_string_buffer,
    sizeof, cast, c_void_p, c_uint32
)
from ctypes.wintypes import (
    BYTE, DWORD, WORD
)

from plyer.facades import CPU


KERNEL = windll.kernel32
ERROR_INSUFFICIENT_BUFFER = 0x0000007A


class CacheType:
    '''
    Win API PROCESSOR_CACHE_TYPE enum.
    '''

    unified = 0
    instruction = 1
    data = 2
    trace = 3


class RelationshipType:
    '''
    Win API LOGICAL_PROCESSOR_RELATIONSHIP enum.
    '''

    processor_core = 0     # logical proc sharing single core
    numa_node = 1          # logical proc sharing single NUMA node
    cache = 2              # logical proc sharing cache
    processor_package = 3  # logical proc sharing physical package
    group = 4              # logical proc sharing processor group
    all = 0xffff           # logical proc info for all groups


class CacheDescriptor(Structure):
    '''
    Win API CACHE_DESCRIPTOR struct.
    '''

    _fields_ = [
        ('Level', BYTE),
        ('Associativity', BYTE),
        ('LineSize', WORD),
        ('Size', DWORD),
        ('Type', DWORD)
    ]


class ProcessorCore(Structure):
    '''
    Win API ProcessorCore struct.
    '''

    _fields_ = [('Flags', BYTE)]


class NumaNode(Structure):
    '''
    Win API NumaNode struct.
    '''

    _fields_ = [('NodeNumber', DWORD)]


class SystemLPIUnion(Union):
    '''
    Win API SYSTEM_LOGICAL_PROCESSOR_INFORMATION union without name.
    '''

    _fields_ = [
        ('ProcessorCore', ProcessorCore),
        ('NumaNode', NumaNode),
        ('Cache', CacheDescriptor),
        ('Reserved', c_ulonglong)
    ]


class SystemLPI(Structure):
    '''
    Win API SYSTEM_LOGICAL_PROCESSOR_INFORMATION struct.
    '''

    _fields_ = [
        ('ProcessorMask', c_ulong),
        ('Relationship', c_ulong),
        ('LPI', SystemLPIUnion)
    ]


class WinCPU(CPU):
    '''
    Implementation of Windows CPU API.
    '''

    @staticmethod
    def _countbits(mask):
        # make sure the correct ULONG_PTR size is used on 64bit
        # https://docs.microsoft.com/en-us/windows/
        # desktop/WinProg/windows-data-types
        # note: not a pointer per-se, != PULONG_PTR
        ulong_ptr = c_ulonglong if sizeof(c_void_p) == 8 else c_ulong
        # note: c_ulonglong only on 64bit, otherwise c_ulong

        # DWORD == c_uint32
        # https://docs.microsoft.com/en-us/windows/
        # desktop/WinProg/windows-data-types
        lshift = c_uint32(sizeof(ulong_ptr) * 8 - 1)
        assert lshift.value in (31, 63), lshift  # 32 or 64 bits - 1

        lshift = lshift.value
        test = 1 << lshift
        assert test % 2 == 0, test

        count = 0
        i = 0
        while i <= lshift:
            i += 1

            # do NOT remove!!!
            # test value has to be %2 == 0,
            # except the last case where the value is 1,
            # so that int(test) == int(float(test))
            # and the mask bit is counted correctly
            assert test % 2 == 0 or float(test) == 1.0, test

            # https://stackoverflow.com/a/1746642/5994041
            # note: useful to print(str(bin(int(...)))[2:])
            count += 1 if (mask & int(test)) else 0
            test /= 2

        return count

    def _logprocinfo(self, relationship):
        get_logical_process_info = KERNEL.GetLogicalProcessorInformation

        # first call with no structure to get the real size of the required
        buff_length = c_ulong(0)
        result = get_logical_process_info(None, byref(buff_length))
        assert not result, result
        error = KERNEL.GetLastError()
        assert error == ERROR_INSUFFICIENT_BUFFER, error
        assert buff_length, buff_length

        # create buffer from the real winapi buffer length
        buff = create_string_buffer(buff_length.value)

        # call again with buffer pointer + the same length as arguments
        result = get_logical_process_info(buff, byref(buff_length))
        assert result, (result, KERNEL.GetLastError())

        # memory size of one LPI struct in the array of LPI structs
        offset = sizeof(SystemLPI)  # ok
        values = {
            key: 0 for key in (
                'relationship', 'mask',
                'L1', 'L2', 'L3'
            )
        }

        for i in range(0, buff_length.value, offset):
            slpi = cast(
                buff[i: i + offset],
                POINTER(SystemLPI)
            ).contents

            if slpi.Relationship != relationship:
                continue

            values['relationship'] += 1
            values['mask'] += self._countbits(slpi.ProcessorMask)

            if slpi.LPI.Cache.Level == 1:
                values['L1'] += 1
            elif slpi.LPI.Cache.Level == 2:
                values['L2'] += 1
            elif slpi.LPI.Cache.Level == 3:
                values['L3'] += 1

        return values

    def _sockets(self):
        # physical CPU sockets (or slots) on motherboard
        return self._logprocinfo(
            RelationshipType.processor_package
        )['relationship']

    def _physical(self):
        # cores
        return self._logprocinfo(
            RelationshipType.processor_core
        )['relationship']

    def _logical(self):
        # cores * threads
        # if hyperthreaded core -> more than one logical processor
        return self._logprocinfo(
            RelationshipType.processor_core
        )['mask']

    def _cache(self):
        # L1, L2, L3 cache count
        result = self._logprocinfo(
            RelationshipType.cache
        )
        return {
            key: result[key]
            for key in result
            if key in ('L1', 'L2', 'L3')
        }

    def _numa(self):
        # numa nodes
        return self._logprocinfo(
            RelationshipType.numa_node
        )['relationship']


def instance():
    '''
    Instance for facade proxy.
    '''
    return WinCPU()


# Resources:
# GetLogicalProcessInformation
# https://msdn.microsoft.com/en-us/library/ms683194(v=vs.85).aspx

# SYSTEM_LOGICAL_PROCESSOR_INFORMATION
# https://msdn.microsoft.com/en-us/library/ms686694(v=vs.85).aspx

# LOGICAL_PROCESSOR_RELATIONSHIP enum (0 - 4, 0xffff)
# https://msdn.microsoft.com/2ada52f0-70ec-4146-9ef7-9af3b08996f9

# CACHE_DESCRIPTOR struct
# https://msdn.microsoft.com/38cfa605-831c-45ef-a99f-55f42b2b56e9

# PROCESSOR_CACHE_TYPE
# https://msdn.microsoft.com/23044f67-e944-43c2-8c75-3d2fba87cb3c

# C example
# https://msdn.microsoft.com/en-us/904d2d35-f419-4e8f-a689-f39ed926644c
