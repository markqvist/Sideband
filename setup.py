import os
import re
import setuptools

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
        raise ValueError(f"Unable to find version string in {version_file}.")

__version__ = get_version()
__variant__ = get_variant()

print("Packaging Sideband "+__version__+" "+__variant__)

setuptools.setup(
    name="sbapp",
    version=__version__,
    author="Mark Qvist",
    author_email="mark@unsigned.io",
    description="LXMF client for Android, Linux and macOS allowing you to communicate with people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://unsigned.io/sideband",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    entry_points= {
        'console_scripts': [
            'sideband=sbapp:main.run',
        ]
    },
    install_requires=['rns>=0.3.11', 'lxmf>=0.1.7', 'kivy==2.1.0', 'plyer'],
    python_requires='>=3.6',
)
