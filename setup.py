import setuptools

__version__ = "0.1.6"
__variant__ = "beta"

with open("README.md", "r") as fh:
    long_description = fh.read()

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
    install_requires=['rns>=0.3.9', 'lxmf>=0.1.7', 'kivy==2.1.0', 'plyer'],
    python_requires='>=3.6',
)
