import ctypes
import os


def NSIterateSearchPaths(directory):
    LibraryPath = ("/System/Library/Frameworks/CoreFoundation.framework/"
                   "Versions/A/CoreFoundation")
    CoreFound = ctypes.cdll.LoadLibrary(LibraryPath)
    NSStartSearchPathEnumeration = CoreFound.NSStartSearchPathEnumeration
    NSGetNextSearchPathEnumeration = CoreFound.NSGetNextSearchPathEnumeration
    PATH_MAX = os.pathconf('/', os.pathconf_names['PC_PATH_MAX'])
    PATH_ENCODING = 'utf8'
    path_buffer = ctypes.create_string_buffer(PATH_MAX)
    # paths = []  <- fixme, possible list of paths in directory
    state = NSStartSearchPathEnumeration(directory, 1)
    while True:
        state = NSGetNextSearchPathEnumeration(state, path_buffer)
        if state == 0:
            break
        path = os.path.expanduser(path_buffer.value.decode(PATH_ENCODING))
        return path
