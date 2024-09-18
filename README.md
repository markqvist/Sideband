Sideband <img align="right" src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg"/>
=========

Sideband is an extensible LXMF messaging client, situational awareness tracker and remote control and monitoring system for Android, Linux, macOS and Windows. It allows you to communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, Encrypted QR Paper Messages, or anything else Reticulum supports.

![Screenshot](https://github.com/markqvist/Sideband/raw/main/docs/screenshots/devices_small.webp)

Sideband is completely free, end-to-end encrypted, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system [LXMF](https://github.com/markqvist/lxmf "LXMF"). There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere. Please read the Guide section included in the program, to get an understanding of how Sideband differs from other messaging systems.

# Functionality & Features

Sideband provides many useful and interesting functions, such as:

- **Secure** and **self-sovereign** messaging using the LXMF protocol over Reticulum.
- **Image** and **file transfers** over all supported mediums.
- **Audio messages** that work even over **LoRa** and **radio links**, thanks to [Codec2](https://github.com/drowe67/codec2/) and [Opus](https://github.com/xiph/opus) encoding.
- Secure and direct P2P **telemetry and location sharing**. No third parties or servers ever have your data.
- Situation display on both online and **locally stored offline maps**.
- Geospatial awareness calculations.
- Exchanging messages through **encrypted QR-codes on paper**, or through messages embedded directly in **lxm://** links.
- Using **Android devices as impromptu Reticulum routers** (*Transport Instances*), for setting up or extending networks easily.
- Remote **command execution and response engine**, with built-in commands, such as `ping`, `signal` reports and `echo`, and **full plug-ing expandability**.
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

For your Android devices, you can install Sideband through F-Droid, by adding the [Between the Borders Repo](https://reticulum.betweentheborders.com/fdroid/repo/), or you can download an [APK on the latest release](https://github.com/markqvist/Sideband/releases/latest) page. Both sources are signed with the same release keys, and can be used interchangably.

After the application is installed on your Android device, it is also possible to pull updates directly through the **Repository** section of the application.

## On Linux

On all Linux-based operating systems, Sideband is available as a `pipx`/`pip` package. This installation method **includes desktop integration**, so that Sideband will show up in your applications menu and launchers. Below are install steps for the most common recent Linux distros. For Debian 11, see the end of this section.

You will first need to install a few dependencies for audio messaging and Codec2 support to work:

```bash
# For Debian (12+), Ubuntu (22.04+) and derivatives
sudo apt install pipx python3-pyaudio python3-dev build-essential libopusfile0 portaudio19-dev codec2 xclip xsel

# For Manjaro and derivatives
pamac install python-pipx python-pyaudio base-devel codec2 xclip xsel

# For Arch and derivatives
sudo pacman -Sy python-pipx python-pyaudio base-devel codec2 xclip xsel

```

Once those are installed, install the Sideband application itself:

```bash
# Finally, install Sideband using pipx:
pipx install sbapp
```

After installation, you can now run Sideband in a number of different ways:

```bash
# If this is the first time installing something with pipx,
# you may need to use the following command, to make your
# installed applications available. You'll probably need
# to close and reopen your terminal after this.
pipx ensurepath

# The first time you run Sideband, you will need to do it
# from the terminal:
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

You can also install Sideband in various alternative ways:

```bash
# Install Sideband via pip instead of pipx:
pip install sbapp

# Or, if pip is externally managed:
pip install sbapp --break-system-packages

# Or, if you intend to run Sideband in headless
# daemon mode, you can also install it without
# any of the normal UI dependencies:
pip install sbapp --no-dependencies

# In the above case, you will still need to
# manually install the RNS and LXMF dependencies:
pip install rns lxmf

# Install Sideband on Debian 11 and derivatives:
sudo apt install python3-pip python3-pyaudio python3-dev build-essential libopusfile0 portaudio19-dev codec2 xclip xsel
pip install sbapp

# On Debian 11, run Sideband manually via the
# terminal once to install desktop integration:
python3 -m sbapp.main
```

## On Raspberry Pi

You can install Sideband on all Raspberry Pi models that support 64-bit operating systems, and can run at least Python version 3.11. Since some of Sideband's dependencies don't have pre-built packages ready for 64-bit ARM processors yet, you'll need to install a few extra packages, that will allow building these while installing.

Aditionally, the `pycodec2` package needs to be installed manually. I have provided a pre-built version, that you can download and install with a single command, or if you don't want to trust my pre-built version, you can [build and install it from source yourself](https://github.com/gregorias/pycodec2/blob/main/DEV.md).

The install instructions below assume that you are installing Sideband on 64-bit Raspberry Pi OS (based on Debian Bookworm). If you're running something else on your Pi, you might need to modify some commands slightly. To install Sideband on Raspberry Pi, follow these steps:

```bash
# First of all, install the required dependencies:
sudo apt install python3-pip python3-pyaudio python3-dev python3-cryptography build-essential libopusfile0 libsdl2-dev libavcodec-dev libavdevice-dev libavfilter-dev portaudio19-dev codec2 libcodec2-1.0 xclip xsel

# If you don't want to compile pycodec2 yourself,
# download the pre-compiled package provided here
wget https://raw.githubusercontent.com/markqvist/Sideband/main/docs/utilities/pycodec2-3.0.1-cp311-cp311-linux_aarch64.whl

# Install it:
pip install ./pycodec2-3.0.1-cp311-cp311-linux_aarch64.whl --break-system-packages

# You can now install Sideband
pip install sbapp --break-system-packages

# Restart your Raspberry Pi
sudo reboot

# Everything is ready! You can now run Sideband
# from the terminal, or from the application menu
sideband
```

## On macOS

On macOS, you can install Sideband with `pip3` or `pipx`. Due to the many different potential Python versions and install paths across macOS versions, the easiest install method is to use `pipx`.

If you don't already have the `pipx` package manager installed, it can be installed via [Homebrew](https://brew.sh/) with `brew install pipx`.

```bash
# Install Sideband and dependencies on macOS using pipx:
pipx install sbapp
pipx ensurepath

# Run it
sideband
```

Or, if you prefer to use `pip` directly, follow the instructions below. In this case, if you have not already installed Python and `pip3` on your macOS system, [download and install](https://www.python.org/downloads/) the latest version first.

```bash
# Install Sideband and dependencies on macOS using pip:
pip3 install sbapp --user --break-system-packages

# Run it:
python3 -m sbapp.main

# If you add your pip install location to
# the PATH environment variable, you can
# also run Sideband simply using:
sideband

```

## On Windows

Even though there is currently not an automated installer, or packaged `.exe` file for Sideband on Windows, you can still install it through `pip`. If you don't already have Python installed, [download and install](https://www.python.org/downloads/) the latest version of Python.

Please note that audio messaging functionality isn't supported on Windows yet. Please support the development if you'd like to see this feature added faster.

**Important!** When asked by the installer, make sure to add the Python program to your PATH environment variables. If you don't do this, you will not be able to use the `pip` installer, or run the `sideband` command.

When Python has been installed, you can open a command prompt and install sideband via `pip`:

```bash
pip install sbapp
```

The Sideband application can now be launched by running the command `sideband` in the command prompt. If needed, you can create a shortcut for Sideband on your desktop or in the start menu.

When running Sideband for the first time, a default Reticulum configuration file will be created, if you don't already have one. If you don't have any existing Reticulum connectivity available locally, you may want to edit the file, located at `C:\Users\USERNAME\.reticulum\config` and manually add an interface that provides connectivity to a wider network. If you just want to connect over the Internet, you can add one of the public hubs on the [Reticulum Testnet](https://reticulum.network/connect.html).

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
- Ethereum
  ```
  0xFDabC71AC4c0C78C95aDDDe3B4FA19d6273c5E73
  ```
- Bitcoin
  ```
  35G9uWVzrpJJibzUwpNUQGQNFzLirhrYAH
  ```
- Ko-Fi: https://ko-fi.com/markqvist

<br/>

# Development Roadmap

- <s>Secure and private location and telemetry sharing</s>
- <s>Including images in messages</s>
- <s>Sending file attachments</s>
- <s>Offline and online maps</s>
- <s>Paper messages</s>
- <s>Using Sideband as a Reticulum Transport Instance</s>
- <s>Encryption keys export and import</s>
- <s>Plugin support for commands, services and telemetry</s>
- <s>Adding Linux .desktop file integration</s>
- <s>Sending voice messages (using Codec2 and Opus)</s>
- Implementing the Local Broadcasts feature
- LXMF sneakernet functionality
- Network visualisation and test tools
- A debug log viewer
- Better message sorting mechanism
- Fix I2P status not being displayed correctly when the I2P router disappears unexpectedly
- Adding a Nomad Net page browser

# License
Unless otherwise noted, this work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

Permission is hereby granted to use Sideband in binary form, for any and all purposes, and to freely distribute binary copies of the program, so long as no payment or compensation is charged or received for such distribution or use.

<img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" align="right">

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


*Device screenshots generated with [deviceframes](https://deviceframes.com). Thanks!*
