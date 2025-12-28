Sideband <img align="right" src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg"/>
=========

*This repository is [a public mirror](./MIRROR.md). All development is happening elsewhere.*

Sideband is an extensible LXMF messaging and LXST telephony client, situational awareness tracker and remote control and monitoring system for Android, Linux, macOS and Windows. It allows you to communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, Encrypted QR Paper Messages, or anything else Reticulum supports.

![Screenshot](https://github.com/markqvist/Sideband/raw/main/docs/screenshots/devices_small.webp)

Sideband is completely free, end-to-end encrypted, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system [LXMF](https://github.com/markqvist/lxmf "LXMF"). There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere. Please read the Guide section included in the program, to get an understanding of how Sideband differs from other messaging systems.

# Functionality & Features

Sideband provides many useful and interesting functions, such as:

- **Secure** and **self-sovereign** messaging and voice calls using the LXMF and LXST protocols over Reticulum.
- **Image** and **file transfers** over all supported mediums.
- **Audio messages** that work even over **LoRa** and **radio links**, thanks to [Codec2](https://github.com/drowe67/codec2/) and [Opus](https://github.com/xiph/opus) encoding.
- Secure and direct P2P **telemetry and location sharing**. No third parties or servers ever have your data.
- The telemetry system is **completely extensible** via [simple plugins](#creating-plugins).
- Situation display on both online and **locally stored offline maps**.
- Geospatial awareness calculations.
- Exchanging messages through **encrypted QR-codes on paper**, or through messages embedded directly in **lxm://** links.
- Using **Android devices as impromptu Reticulum routers** (*Transport Instances*), for setting up or extending networks easily.
- Remote **command execution and response engine**, with built-in commands, such as `ping`, `signal` reports and `echo`, and **full plugin expandability**.
- Remote **telemetry querying**, with strong, secure and cryptographically robust authentication and control.
- **Plugin system** that allows you to easily **create your own commands**, services and telemetry sources.

Sideband is fully compatible with other LXMF clients, such as [MeshChat](https://github.com/liamcottle/reticulum-meshchat), and [Nomad Network](https://github.com/markqvist/nomadnet). The Nomad Network client also allows you to easily host Propagation Nodes for your LXMF network, and more.

# Installation

Sideband can run on most computing devices, but installation methods vary by device type and operating system. For installation instructions, please find the relevant section below.

- [Android](#on-android)
- [Linux](#on-linux)
- [Raspberry Pi](#on-raspberry-pi)
- [MacOS](#on-macos)
- [Windows](#on-windows)

## On Android

For your Android devices, you can download an [APK on the latest release page](https://github.com/markqvist/Sideband/releases/latest).

After the application is installed on your Android device, it is also possible to pull updates directly through the **Repository** section of the application.

The Sideband APK file is always signed with a consistent signing certificate directly at build time. Before installing it for the first time, you can verify that the APK has not been modified, by checking that the APK file's signing certificate matches these hashes:

```text
SHA-256 digest: 1c65f01f586a2b73ac4eb8bf48730b3899d046447185fd9d005685a4af20cdea
SHA-1 digest: 4ab9269c320c72f4e4057ec7ea5acade320c2a48
MD5 digest: 09afff8c505089a544ad2bf371c29422
```

Sideband will never be released on app store platforms that does not support complete control of the APK signing directly from the developer. If you download Sideband from any other source than this repository, and the certificate hashes do not match, **do not install it**.

The Android version of Sideband has been carefully set up to **not** use any Android APIs or functionality that are dependent on Google (or other vendor-specific) components or libraries. It uses only raw Android OS APIs, and accesses them directly, instead of through "compatibility", "support" or "helper" libraries, which can often hijack application data flow into privacy-compromising pipelines controlled by Google or other vendors.

This also means that Sideband is designed to be fully compatible with custom (and more privacy-friendly) Android versions and ROMs, such as GrapheneOS, de-googled devices and other custom ROMs.

## On Linux

On all Linux-based operating systems, Sideband is available as a `pip`/`pipx` package. You can either pull and install Sideband directly from the `pip` repository, or download and install locally using `whl` package from the [latest release page](https://github.com/markqvist/Sideband/releases/latest).

This installation method **includes desktop integration**, so that Sideband will show up in your applications menu and launchers. Below are install steps for the most common recent Linux distros. For Debian 11, see the end of this section.

#### Basic Installation
You will first need to install a few dependencies for voice calls, audio messaging and Codec2 support to work:

```bash
# For Debian 13+, Ubuntu 24.04+ and derivatives
sudo apt install python3-pip python3-pyaudio libopusfile0 codec2 xclip xsel

# For Debian 12+, Ubuntu 22.04+ and derivatives
sudo apt install python3-pip python3-pyaudio python3-dev build-essential libopusfile0 portaudio19-dev codec2 xclip xsel

# For Manjaro and derivatives
pamac install python-pyaudio opusfile codec2 xclip xsel

# For Arch and derivatives
sudo pacman -Sy python-pyaudio opusfile codec2 xclip xsel

```

Once those are installed, install the Sideband application itself:

```bash
# Finally, install Sideband using pip:
pip install sbapp --break-system-packages

# If Sideband does not show up in your application menu
# or as an executable command in your terminal, reboot
# your computer.
sudo reboot
```

After installation, you can now run Sideband in a number of different ways:

```bash
# The first time you run Sideband, you will need to do it
# from the terminal, for the application launcher item to
# show up. On some distros you may also need to log out
# and back in again, or simply reboot the machine for the
# application entry to show up in your menu.
sideband

# At the first launch, it will add an application icon
# to your launcher or apps menu. You may need to log out
# of your session, and back in for the application to
# show up in your launcher, depending on your distro.

# You can also run Sideband in headless daemon
# mode, for example as a telemetry collector:
sideband --daemon

# You can also run Sideband with more verbose
# log output enabled:
sideband -v
```

If you do not already have Reticulum connectivity set up on your computer or local network, you will probably want to edit the Reticulum configuration file at `~/.reticulum/config` and [add any interfaces](https://reticulum.network/manual/interfaces.html) you need for connectivity.

#### Advanced Installation
You can also install Sideband in various alternative ways:

```bash
# Install Sideband via pipx instead of pip:
pipx install sbapp

# Or, if you intend to run Sideband in headless
# daemon or console mode, you can also install
# it without any of the normal UI dependencies:
pip install sbapp --no-dependencies

# In the case of using --no-dependencies, you
# will still need to manually install the RNS
# and LXMF dependencies:
pip install rns lxmf

# Dependencies can vary slightly on older OS
# versions, due to different package names.

# Install Sideband on Debian 11 and derivatives:
sudo apt install python3-pip python3-pyaudio python3-dev build-essential libopusfile0 portaudio19-dev codec2 xclip xsel
pip install sbapp

# On Debian 11, run Sideband manually via the
# terminal once to install desktop integration:
python3 -m sbapp.main
```

## On Raspberry Pi

You can install Sideband on all Raspberry Pi models that support 64-bit operating systems, and can run at least Python version 3.11.

The install instructions below assume that you are installing Sideband on 64-bit Raspberry Pi OS (based on Debian 13 "Trixie" or later). If you're running something else on your Pi, you might need to modify some commands slightly.

To install Sideband on Raspberry Pi with full support for voice calls, audio messages and Codec2, follow these steps:

```bash
# First of all, install the dependencies required
# for audio processing and voice calls.
#
# On Raspberry Pi OS "Trixie" (based on Debian 13)
# or newer, install these packages:
sudo apt install python3-pyaudio codec2 xclip xsel

# You can now install Sideband
pip install sbapp --break-system-packages

# Restart your Raspberry Pi to ensure the program
# is available in your PATH and application menus:
sudo reboot

# Everything is ready! You can now run Sideband
# from the terminal, or from the application menu:
sideband
```

If you're using an older version of Raspberry Pi OS, you will need to install these dependencies instead, before installing Sideband:

```bash
# Package dependencies for Raspberry Pi OS based
# on Debian 12 Bookworm
sudo apt install python3-pip python3-pyaudio python3-dev python3-cryptography build-essential libopusfile0 libsdl2-dev libavcodec-dev libavdevice-dev libavfilter-dev portaudio19-dev codec2 libcodec2-1.0 xclip xsel
```

If you do not already have Reticulum connectivity set up on your computer or local network, you will probably want to edit the Reticulum configuration file at `~/.reticulum/config` and [add any interfaces](https://reticulum.network/manual/interfaces.html) you need for connectivity.

## On macOS

To install Sideband on macOS, you have two options available:

1. An easy to install pre-built disk image package
2. A source package install for more advanced setups

#### Prebuilt Executable

You can download a disk image with Sideband for macOS (ARM and Intel) from the [latest release page](https://github.com/markqvist/Sideband/releases/latest). Simply mount the downloaded disk image, drag `Sideband` to your applications folder, and run it.

**Please note!** If you have application install restrictions enabled on your macOS install, or have restricted your system to only allow installation of application from the Apple App Store, you will need to create an exception for Sideband. The Sideband application will *never* be distributed with an Apple-controlled digital signature, as this will allow Apple to simply disable Sideband from running on your system if they decide to do so, or are forced to by authorities or other circumstances.

If you install Sideband from the DMG file, it is still recommended to install the `rns` package via the `pip` or `pipx` package manager, so you can use the RNS utility programs, like `rnstatus` to see interface and connectivity status from the terminal. If you already have Python and `pip` installed on your system, simply open a terminal window and use one of the following commands:

```bash
# Install Reticulum and utilities with pip:
pip3 install rns --user

# On some versions, you may need to use the
# flag --break-system-packages to install:
pip3 install rns --user --break-system-packages
```

If you do not have Python and `pip` available, [download and install it](https://www.python.org/downloads/) first.

If you do not already have Reticulum connectivity set up on your computer or local network, you will probably want to edit the Reticulum configuration file at `~/.reticulum/config` and [add any interfaces](https://reticulum.network/manual/interfaces.html) you need for connectivity.

#### Source Package Install

For more advanced setups, including the ability to run Sideband in headless daemon mode, enable debug logging output, configuration import and export and more, you may want to install it from the source package via `pip` instead.

To install Sideband via `pip`, follow these instructions:

```bash
# Install Sideband and dependencies on macOS using pip:
pip3 install sbapp --user

# Or, if your Python environment is externally managed:
pip3 install sbapp --user --break-system-packages

# Important note! On some macOS versions, programs that
# were installed with pip does not get added to your
# PATH environment variable. If this is the case, pip
# will print out a warning about it during installation.
# In that case, you will have to manually add the path
# shown in the installation warning to your PATH, before
# you can run commands such as "sideband" or "rnstatus"
# from your shell.

# Run Sideband from the terminal:
#################################
sideband
# or
python3 -m sbapp.main

# Enable debug logging:
#################################
sideband -v
# or
python3 -m sbapp.main -v

# Start Sideband in daemon mode:
#################################
sideband -d
# or
python3 -m sbapp.main -d

# If Python and pip was installed correctly,
# you can simply use the "sideband" command
# directly. Otherwise, you will manually
# need to add the pip binaries directory to
# your PATH environment variable, or start
# Sideband via the "python3 -m sbapp.main"
# syntax.

```

## On Windows

To install Sideband on Windows, you have two options available:

1. An easy to install pre-built executable package
2. A source package install for more advanced setups

#### Prebuilt Executable

Simply download the packaged Windows ZIP file from the [latest release page](https://github.com/markqvist/Sideband/releases/latest), unzip the file, and run `Sideband.exe` from the unzipped directory. You can create desktop or start menu shortcuts from this executable if needed.

When running Sideband for the first time, a default Reticulum configuration file will be created, if you don't already have one. If you don't have any existing Reticulum connectivity available locally, you may want to edit the file, located at `C:\Users\USERNAME\.reticulum\config` and manually add an interface that provides connectivity to a wider network. If you just want to connect over the Internet, you can add one of the public hubs on the [Reticulum Testnet](https://reticulum.network/connect.html).

#### Installing Reticulum Utilities

Though the ZIP file contains everything necessary to run Sideband, it is also recommended to install the Reticulum command line utilities separately, so that you can use commands like `rnstatus` and `rnsd` from the command line. This will make it easier to manage Reticulum connectivity on your system. If you do not already have Python installed on your system, [download and install it](https://www.python.org/downloads/) first.

**Important!** When asked by the installer, make sure to add the Python program to your `PATH` environment variables. If you don't do this, you will not be able to use the `pip` installer, or run any of the installed commands. When Python has been installed, you can open a command prompt and install the Reticulum package via `pip`:

```bash
pip install rns
```

#### Source Package Install

For more advanced setups, including the ability to run Sideband in headless daemon mode, enable debug logging output, configuration import and export and more, you may want to install it from the source package via `pip` instead.

In this case, you will need to [download and install the latest supported version of Python](https://www.python.org/downloads/release/python-3127/) (currently Python 3.12.7), since very latest Python release, Python 3.13 is currently **not** compatible with the Kivy framework, that Sideband uses to render its user interface. The binary package already includes a compatible Python version, so if you are running Sideband from that, there is no need to install a specific version of Python.

When Python has been installed, you can open a command prompt and install Sideband via `pip`:

```bash
pip install sbapp
```

The Sideband application can now be launched by running the command `sideband` in the command prompt. If needed, you can create a shortcut for Sideband on your desktop or in the start menu.

Since this installation method automatically installs the `rns` and `lxmf` packages as well, you will also have access to using all the included RNS and LXMF utilities like `rnstatus`, `rnsd` and `lxmd` on your system.

# Creating Plugins

Sideband features a flexible and extensible plugin system, that allows you to hook all kinds of control, status reporting, command execution and telemetry collection into the LXMF messaging system. Plugins can be created as either *Telemetry*, *Command* or *Service* plugins, for different use-cases.

To create plugins for Sideband, you can find a variety of [code examples](https://github.com/markqvist/Sideband/tree/main/docs/example_plugins) in this repository, that you can use as a basis for writing your own plugins. The example plugins include:

- [Custom telemetry](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/telemetry.py)
- [Getting BME280 temperature, humidity and pressure](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/bme280_telemetry.py)
- [Basic commands](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/basic.py)
- [Location telemetry from GPSd on Linux](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/gpsd_location.py)
- [Location telemetry from Windows Location Provider](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/windows_location.py)
- [Getting statistics from your LXMF propagation node](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/lxmd_telemetry.py)
- [Viewing cameras and streams](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/view.py)
- [Fetching an XKCD comic](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/comic.py)
- [Creating a service plugin](https://github.com/markqvist/Sideband/blob/main/docs/example_plugins/service.py)

For creating telemetry plugins, Sideband includes 20+ built-in sensor types to chose from, for representing all kinds telemetry data. If none of those fit your needs, there is a `Custom` sensor type, that can include any kind of data.

Command plugins allow you to define any kind of action or command to be run when receiving command messages from other LXMF clients. In the example directory, you will find various command plugin templates, for example for viewing security cameras or webcams through Sideband.

Service plugins allow you to integrate any kind of service, bridge or other system into Sideband, and have that react to events or state changes in Sideband itself.

# Paper Messaging Example

You can try out the paper messaging functionality by using the following QR-code. It is a paper message sent to the LXMF address `6b3362bd2c1dbf87b66a85f79a8d8c75`. To be able to decrypt and read the message, you will need to import the following base32-encoded Reticulum Identity into the app:

`3BPTDTQCRZPKJT3TXAJCMQFMOYWIM3OCLKPWMG4HCF2T4CH3YZHVNHNRDU6QAZWV2KBHMWBNT2C62TQEVC5GLFM4MN25VLZFSK3ADRQ=`

You can import the identity into Sideband in the **Encryption Keys** part of the program. After the you have imported the identity, you can scan the following QR-code and open it in the app, where it will be decrypted and added to your messages.

<p align="center"><img width="50%" src="https://raw.githubusercontent.com/markqvist/LXMF/master/docs/paper_msg_test.png"/></p>

You can also find the entire message in <a href="lxm://azNivSwdv4e2aoX3mo2MdTAozuI7BlzrLlHULmnVgpz3dNT9CMPVwgywzCJP8FVogj5j_kU7j7ywuvBNcr45kRTrd19c3iHenmnSDe4VEd6FuGsAiT0Khzl7T81YZHPTDhRNp0FdhDE9AJ7uphw7zKMyqhHHxOxqrYeBeKF66gpPxDceqjsOApvsSwggjcuHBx9OxOBy05XmnJxA1unCKgvNfOFYc1T47luxoY3c0dLOJnJPwZuFRytx2TXlQNZzOJ28yTEygIfkDqEO9mZi5lgev7XZJ0DvgioQxMIyoCm7lBUzfq66zW3SQj6vHHph7bhr36dLOCFgk4fZA6yia2MlTT9KV66Tn2l8mPNDlvuSAJhwDA_xx2PN9zKadCjo9sItkAp8r-Ss1CzoUWZUAyT1oDw7ly6RrzGBG-e3eM3CL6u1juIeFiHby7_3cON-6VTUuk4xR5nwKlFTu5vsYMVXe5H3VahiDSS4Q1aqX7I">this link</a>:

`lxm://azNivSwdv4e2aoX3mo2MdTAozuI7BlzrLlHULmnVgpz3dNT9CMPVwgywzCJP8FVogj5j_kU7j7ywuvBNcr45kRTrd19c3iHenmnSDe4VEd6FuGsAiT0Khzl7T81YZHPTDhRNp0FdhDE9AJ7uphw7zKMyqhHHxOxqrYeBeKF66gpPxDceqjsOApvsSwggjcuHBx9OxOBy05XmnJxA1unCKgvNfOFYc1T47luxoY3c0dLOJnJPwZuFRytx2TXlQNZzOJ28yTEygIfkDqEO9mZi5lgev7XZJ0DvgioQxMIyoCm7lBUzfq66zW3SQj6vHHph7bhr36dLOCFgk4fZA6yia2MlTT9KV66Tn2l8mPNDlvuSAJhwDA_xx2PN9zKadCjo9sItkAp8r-Ss1CzoUWZUAyT1oDw7ly6RrzGBG-e3eM3CL6u1juIeFiHby7_3cON-6VTUuk4xR5nwKlFTu5vsYMVXe5H3VahiDSS4Q1aqX7I`

On operating systems that allow for registering custom URI-handlers, you can click the link, and it will be decoded directly in your LXMF client. This works with Sideband on Android.

# Support Sideband Development
You can help support the continued development of open, free and private communications systems by donating via one of the following channels:

- Monero:
  ```
  84FpY1QbxHcgdseePYNmhTHcrgMX4nFfBYtz2GKYToqHVVhJp8Eaw1Z1EedRnKD19b3B8NiLCGVxzKV17UMmmeEsCrPyA5w
  ```
- Bitcoin
  ```
  bc1p4a6axuvl7n9hpapfj8sv5reqj8kz6uxa67d5en70vzrttj0fmcusgxsfk5
  ```
- Ethereum
  ```
  0xae89F3B94fC4AD6563F0864a55F9a697a90261ff
  ```
- Liberapay: https://liberapay.com/Reticulum/

- Ko-Fi: https://ko-fi.com/markqvist


<br/>

# License
Unless otherwise noted, this work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

Permission is hereby granted to use Sideband in binary form, for any and all purposes, and to freely distribute binary copies of the program, so long as no payment or compensation is charged or received for such distribution or use.

<img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" align="right">

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


*Device screenshots generated with [deviceframes](https://deviceframes.com). Thanks!*
