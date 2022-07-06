import setuptools

from main.py import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sideband",
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
            'sideband=main:main',
        ]
    },
    install_requires=['lxmf'],
    python_requires='>=3.6',
)
