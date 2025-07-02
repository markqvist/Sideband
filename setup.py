import os
import re
import setuptools
from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_version() -> str:
    version_file = os.path.join(
        os.path.dirname(__file__), "sbapp", "main.py"
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
        os.path.dirname(__file__), "sbapp", "main.py"
    )

    version_file_data = open(version_file, "rt", encoding="utf-8").read()
    version_regex = r"(?<=^__variant__ = ['\"])[^'\"]+(?=['\"]$)"
    try:
        version = re.findall(version_regex, version_file_data, re.M)[0]
        return version
    except IndexError:
        return None

__version__ = get_version()
__variant__ = get_variant()

def glob_paths(pattern):
    out_files = []
    src_path = os.path.join(os.path.dirname(__file__), "sbapp/kivymd")

    for root, dirs, files in os.walk(src_path):
        for file in files:
            if file.endswith(pattern):
                filepath = os.path.join(str(Path(*Path(root).parts[1:])), file)
                out_files.append(filepath.split(f"kivymd{os.sep}")[1])

    return out_files

def glob_share():
    out_files = []
    src_path = os.path.join(os.path.dirname(__file__), "sbapp/share")
    print(src_path)

    for root, dirs, files in os.walk(src_path):
        for file in files:
            filepath = os.path.join(str(Path(*Path(root).parts[1:])), file)
            
            if not "mirrors/unsigned.io" in str(filepath):
                out_files.append(filepath.split(f"sbapp{os.sep}")[1])

    return out_files

packages = setuptools.find_packages(
    exclude=[
        "sbapp.plyer.platforms.android",
        "sbapp.kivymd.tools"
        "sbapp.kivymd.tools.*"
    ])

package_data = {
"": [
    "assets/*",
    "assets/fonts/*",
    "assets/geoids/*",
    "kivymd/fonts/*",
    "kivymd/images/*",
    "kivymd/*",
    "mapview/icons/*",
    *glob_share(),
    *glob_paths(".kv")
    ]
}

variant_str = ""
if __variant__:
    variant_str = " "+__variant__
print("Packaging Sideband "+__version__+variant_str)

setuptools.setup(
    name="sbapp",
    version=__version__,
    author="Mark Qvist",
    author_email="mark@unsigned.io",
    description="LXMF client for Android, Linux and macOS allowing you to communicate with people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://unsigned.io/sideband",
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    data_files = [
        ('share/applications', ['sbapp/assets/io.unsigned.sideband.desktop']),
        ('share/icons/hicolor/512x512/apps', ['sbapp/assets/io.unsigned.sideband.png']),
    ],
    entry_points= {
        'console_scripts': [
            'sideband=sbapp:main.run',
        ]
    },
    install_requires=[
        "rns>=0.9.6",
        "lxmf>=0.7.1",
        "kivy>=2.3.0",
        "pillow>=10.2.0",
        "qrcode",
        "materialyoucolor>=2.0.7",
        "ffpyplayer",
        "sh",
        "numpy<=1.26.4",
        "lxst>=0.3.0",
        "mistune>=3.0.2",
        "beautifulsoup4",
        "pycodec2;sys.platform!='Windows' and sys.platform!='win32' and sys.platform!='darwin'",
        "pyaudio;sys.platform=='linux'",
        "pyobjus;sys.platform=='darwin'",
        "pyogg;sys.platform=='Windows' and sys.platform!='win32'",
        "audioop-lts>=0.2.1;python_version>='3.13'"
    ],
    python_requires='>=3.7',
)
