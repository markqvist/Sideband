import os
import re
import setuptools
import cx_Freeze
from pathlib import Path

build_appimage = True

def get_version() -> str:
    version_file = os.path.join(
        os.path.dirname(__file__), "main.py"
    )

    version_file_data = open(version_file, "rt", encoding="utf-8").read()
    version_regex = r"(?<=^__version__ = ['\"])[^'\"]+(?=['\"]$)"
    try:
        version = re.findall(version_regex, version_file_data, re.M)[0]
        return version
    except IndexError:
        raise ValueError(f"Unable to find version string in {version_file}.")

def get_variant() -> str:
    version_file = os.path.join(
        os.path.dirname(__file__), "main.py"
    )

    version_file_data = open(version_file, "rt", encoding="utf-8").read()
    version_regex = r"(?<=^__variant__ = ['\"])[^'\"]+(?=['\"]$)"
    try:
        version = re.findall(version_regex, version_file_data, re.M)[0]
        return version
    except IndexError:
        raise ValueError(f"Unable to find version string in {version_file}.")

__version__ = get_version()
__variant__ = get_variant()

def glob_paths(pattern):
    out_files = []
    src_path = os.path.join(os.path.dirname(__file__), "kivymd")

    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith(pattern):
                filepath = os.path.join(str(Path(*Path(root).parts[1:])), file)
                out_files.append(filepath.split(f"kivymd{os.sep}")[1])

    return out_files

package_data = {
"": [
    "assets/*",
    "assets/fonts/*",
    "assets/geoids/*",
    "kivymd/fonts/*",
    "kivymd/images/*",
    "kivymd/*",
    "mapview/icons/*",
    *glob_paths(".kv")
    ]
}

print("Freezing Sideband "+__version__+" "+__variant__)

if build_appimage:
    global_excludes = [".buildozer", "build", "dist"]
    # Dependencies are automatically detected, but they might need fine-tuning.
    appimage_options = {
        "target_name": "Sideband",
        "target_version": __version__+" "+__variant__,
        "include_files": [],
        "excludes": [],
        "packages": ["kivy"],
        "zip_include_packages": [],
        "bin_path_excludes": global_excludes,
    }

    cx_Freeze.setup(
        name="Sideband",
        version=__version__,
        author="Mark Qvist",
        author_email="mark@unsigned.io",
        url="https://unsigned.io/sideband",
        executables=[
            cx_Freeze.Executable(
                script="main.py",
                base="console",
                target_name="Sideband",
                shortcut_name="Sideband",
                icon="assets/icon.png",
                copyright="Copyright (c) 2024 Mark Qvist",
            ),
        ],
        options={"build_appimage": appimage_options},
    )