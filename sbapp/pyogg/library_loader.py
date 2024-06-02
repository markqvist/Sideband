import ctypes
import ctypes.util
import os
import sys
import platform
from typing import (
    Optional,
    Dict,
    List
)

_here = os.path.dirname(__file__)

class ExternalLibraryError(Exception):
    pass

architecture = platform.architecture()[0]

_windows_styles = ["{}", "lib{}", "lib{}_dynamic", "{}_dynamic"]

_other_styles = ["{}", "lib{}"]

if architecture == "32bit":
    for arch_style in ["32bit", "32" "86", "win32", "x86", "_x86", "_32", "_win32", "_32bit"]:
        for style in ["{}", "lib{}"]:
            _windows_styles.append(style.format("{}"+arch_style))
            
elif architecture == "64bit":
    for arch_style in ["64bit", "64" "86_64", "amd64", "win_amd64", "x86_64", "_x86_64", "_64", "_amd64", "_64bit"]:
        for style in ["{}", "lib{}"]:
            _windows_styles.append(style.format("{}"+arch_style))


run_tests = lambda lib, tests: [f(lib) for f in tests]

# Get the appropriate directory for the shared libraries depending 
# on the current platform and architecture
platform_ = platform.system()
lib_dir = None
if platform_ == "Darwin":
    lib_dir = "libs/macos"
elif platform_ == "Windows":
    if architecture == "32bit":
        lib_dir = "libs/win32"
    elif architecture == "64bit":
        lib_dir = "libs/win_amd64"


class Library:
    @staticmethod
    def load(names: Dict[str, str], paths: Optional[List[str]] = None, tests = []) -> Optional[ctypes.CDLL]:
        lib = InternalLibrary.load(names, tests)
        if lib is None:
            lib = ExternalLibrary.load(names["external"], paths, tests)
        return lib
        

class InternalLibrary:
    @staticmethod
    def load(names: Dict[str, str], tests) -> Optional[ctypes.CDLL]:
        # If we do not have a library directory, give up immediately
        if lib_dir is None:
            return None
            
        # Get the appropriate library filename given the platform
        try:
            name = names[platform_]
        except KeyError:
            return None

        # Attempt to load the library from here
        path = _here + "/" + lib_dir + "/" + name 
        try:
            lib = ctypes.CDLL(path)
        except OSError as e:
            return None

        # Check that the library passes the tests
        if tests and all(run_tests(lib, tests)):
            return lib

        # Library failed tests
        return None
        
# Cache of libraries that have already been loaded
_loaded_libraries: Dict[str, ctypes.CDLL] = {}

class ExternalLibrary:
    @staticmethod
    def load(name, paths = None, tests = []):
        if name in _loaded_libraries:
            return _loaded_libraries[name]
        if sys.platform == "win32":
            lib = ExternalLibrary.load_windows(name, paths, tests)
            _loaded_libraries[name] = lib
            return lib
        else:
            lib = ExternalLibrary.load_other(name, paths, tests)
            _loaded_libraries[name] = lib
            return lib

    @staticmethod
    def load_other(name, paths = None, tests = []):
        os.environ["PATH"] += ";" + ";".join((os.getcwd(), _here))
        if paths: os.environ["PATH"] += ";" + ";".join(paths)

        for style in _other_styles:
            candidate = style.format(name)
            library = ctypes.util.find_library(candidate)
            if library:
                try:
                    lib = ctypes.CDLL(library)
                    if tests and all(run_tests(lib, tests)):
                        return lib
                except:
                    pass

    @staticmethod
    def load_windows(name, paths = None, tests = []):
        os.environ["PATH"] += ";" + ";".join((os.getcwd(), _here))
        if paths: os.environ["PATH"] += ";" + ";".join(paths)
        
        not_supported = [] # libraries that were found, but are not supported
        for style in _windows_styles:
            candidate = style.format(name)
            library = ctypes.util.find_library(candidate)
            if library:
                try:
                    lib = ctypes.CDLL(library)
                    if tests and all(run_tests(lib, tests)):
                        return lib
                    not_supported.append(library)
                except WindowsError:
                    pass
                except OSError:
                    not_supported.append(library)
            

        if not_supported:
            raise ExternalLibraryError("library '{}' couldn't be loaded, because the following candidates were not supported:".format(name)
                                 + ("\n{}" * len(not_supported)).format(*not_supported))

        raise ExternalLibraryError("library '{}' couldn't be loaded".format(name))

        

        
