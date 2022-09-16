import ctypes
from ctypes import (
    Structure, cdll, sizeof,
    c_int8, c_int16, c_size_t
)
from ctypes.util import find_library
import platform

ERROR_DICT = {
    "0": "IOKit Framework not found, is this OSX?",
    "-1": "No SMCMotionSensor service",
    "-2": "No sms device",
    "-3": "Could not open motion sensor device",
    "-4": "Did not receive any coordinates"
}

IOKit = cdll.LoadLibrary(find_library('IOKit'))


class data_structure(Structure):
    _fields_ = [
        ('x', c_int16),
        ('y', c_int16),
        ('z', c_int16),
        ('pad', c_int8 * 34),
    ]


void_p = ctypes.POINTER(ctypes.c_int)

kern_return_t = ctypes.c_int
KERN_SUCCESS = 0
KERN_FUNC = 5  # SMC Motion Sensor on MacBook Pro

mach_port_t = void_p
MACH_PORT_NULL = 0

io_object_t = ctypes.c_int
io_object_t = ctypes.c_int
io_iterator_t = void_p
io_object_t = void_p
io_connect_t = void_p
IOItemCount = ctypes.c_uint

CFMutableDictionaryRef = void_p


def is_os_64bit():
    return platform.machine().endswith('64')


def read_sms():
    result = kern_return_t()
    masterPort = mach_port_t()

    result = IOKit.IOMasterPort(MACH_PORT_NULL, ctypes.byref(masterPort))

    IOKit.IOServiceMatching.restype = CFMutableDictionaryRef
    matchingDictionary = IOKit.IOServiceMatching("SMCMotionSensor")

    iterator = io_iterator_t()
    result = IOKit.IOServiceGetMatchingServices(
        masterPort, matchingDictionary,
        ctypes.byref(iterator)
    )

    if (result != KERN_SUCCESS):
        raise ("No coordinates received!")
        return -1, None

    IOKit.IOIteratorNext.restype = io_object_t
    smsDevice = IOKit.IOIteratorNext(iterator)

    if not smsDevice:
        return -2, None

    dataPort = io_connect_t()
    result = IOKit.IOServiceOpen(
        smsDevice, IOKit.mach_task_self(),
        0, ctypes.byref(dataPort)
    )

    if (result != KERN_SUCCESS):
        return -3, None

    inStructure = data_structure()
    outStructure = data_structure()

    if(is_os_64bit() or hasattr(IOKit, 'IOConnectCallStructMethod')):
        structureInSize = IOItemCount(sizeof(data_structure))
        structureOutSize = c_size_t(sizeof(data_structure))

        result = IOKit.IOConnectCallStructMethod(
            dataPort, KERN_FUNC,
            ctypes.byref(inStructure), structureInSize,
            ctypes.byref(outStructure), ctypes.byref(structureOutSize)
        )
    else:
        structureInSize = IOItemCount(sizeof(data_structure))
        structureOutSize = IOItemCount(sizeof(data_structure))

        result = IOKit.IOConnectMethodStructureIStructureO(
            dataPort, KERN_FUNC,
            structureInSize, ctypes.byref(structureOutSize),
            ctypes.byref(inStructure), ctypes.byref(outStructure)
        )

    IOKit.IOServiceClose(dataPort)

    if (result != KERN_SUCCESS):
        return -4, None

    return 1, outStructure


def get_coord():
    if not IOKit:
        raise Exception(ERROR_DICT["0"])

    ret, data = read_sms()

    if (ret > 0):
        if(data.x):
            return (data.x, data.y, data.z)
        else:
            return (None, None, None)
    else:
        raise Exception(ERROR_DICT[str(ret)])
