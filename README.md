Sideband <img align="right" src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg"/>
=========

Sideband is an extensible LXMF messaging client, situational awareness tracker and remote control and monitoring system for Android, Linux, macOS and Windows. It allows you to communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, Encrypted QR Paper Messages, or anything else Reticulum supports.

![Screenshot](https://github.com/markqvist/Sideband/raw/main/docs/screenshots/devices_small.webp)

Sideband is completely free, end-to-end encrypted, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system [LXMF](https://github.com/markqvist/lxmf "LXMF"). There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere. Please read the Guide section included in the program, to get an understanding of how Sideband differs from other messaging systems.

Sideband provides many useful and interesting functions, such as:

- Secure and self-sovereign messaging using the LXMF protocol over Reticulum.
- Image and file transfers over all supported mediums.
- Audio messages that work even over LoRa and radio links, thanks to [Codec2](https://github.com/drowe67/codec2/) and [Opus](https://github.com/xiph/opus) encoding.
- Secure and direct P2P telemetry and location sharing. No third parties or servers ever have your data.
- Situation display on both online and locally stored offline maps.
- Geospatial awareness calculations.
- Exchanging messages through encrypted QR-codes on paper, or through messages embedded directly in **lxm://** links.
- Using Android devices as impromptu Reticulum routers (*Transport Instances*), for setting up or extending networks easily.
- Remote command execution and response engine, with built-in commands, such as `ping`, `signal` reports and `echo`.
- Remote telemetry querying, with strong, secure and cryptographically robust authentication and control.
- Plugin system that allows you to easily create your own commands, services and telemetry sources.

Sideband is fully compatible with other LXMF clients, such as [MeshChat](https://github.com/liamcottle/reticulum-meshchat), and [Nomad Network](https://github.com/markqvist/nomadnet). The Nomad Network client also allows you to easily host Propagation Nodes for your LXMF network, and more.

## Installation On Android

For your Android devices, you can install Sideband through F-Droid, by adding the [Between the Borders Repo](https://reticulum.betweentheborders.com/fdroid/repo/), or you can download an [APK on the latest release](https://github.com/markqvist/Sideband/releases/latest) page. Both sources are signed with the same release keys, and can be used interchangably.

After the application is installed on your Android device, it is also possible to pull updates directly through the **Repository** section of the application.

## Installation On Linux

On all Linux-based operating systems, Sideband is available as a `pip` package. This installation method **includes desktop integration**, so that Sideband will show up in your applications menu and launchers. Depending on your system, you may need to install the `python-pyaudio` or `python3-pyaudio` package for audio messaging support. Make sure you have Python and `pip` installed (default on most modern distributions), and run:

```bash
# Depending on your distribution, you may need
# to install the pyaudio package via the package
# manager included in your distribution, with
# a command like one of the following:

pamac install python-pyaudio     # Manjaro
sudo pacman -Sy python-pyaudio   # Arch
sudo apt install python3-pyaudio # Debian and derivatives

# Install the Sideband application:
pip install sbapp

# Find the Sideband application in your launcher,
# or run it directly from the command line:
sideband

# You can also run Sideband with more verbose
# log output enabled:
sideband -v

# You can also run Sideband in headless daemon
# mode, for example as a telemetry collector:
sideband --daemon

# If you intend to run Sideband in headless
# daemon mode, you can also install it without
# any of the normal UI dependencies:
pip install sbapp --no-dependencies

# In this case, you will still need to manually
# install the minimum RNS and LXMF dependencies:
pip install rns lxmf

```

**Please Note!** If you are using an operating system that blocks normal user package installation via `pip`, it's easy to permanently return `pip` to normal behaviour by editing the `~/.config/pip/pip.conf` file, and adding the following directive in the `[global]` section:

```text
[global]
break-system-packages = true
```

You can also simply add the `--break-system-packages` directive on a per-installation basis. For example, on a system that blocks normal user package installation, you can install Sideband by running `pip install sbapp --break-system-packages`.

## Installation On macOS

A DMG file containing a macOS app bundle is available on the [latest release](https://github.com/markqvist/Sideband/releases/latest) page.

Alternatively, you can install Sideband with ``pip3`` on macOS:

```bash
# Install Sideband and dependencies on macOS:
pip3 install sbapp

# Run it:
python3 -m sbapp.main

# If you add your pip install location to
# the PATH environment variable, you can
# also run Sideband simply using:
sideband

```

If you have not already installed Python and `pip3` on your macOS system, [download and install](https://www.python.org/downloads/) the latest version first.

## Installation On Windows

Even though there is currently not an automated installer, or packaged `.exe` file for Sideband on Windows, you can still install it through `pip`. If you don't already have Python installed, [download and install](https://www.python.org/downloads/) the latest version of Python.

**Important!** When asked by the installer, make sure to add the Python program to your PATH environment variables. If you don't do this, you will not be able to use the `pip` installer, or run the `sideband` command.

When Python has been installed, you can open a command prompt and install sideband via `pip`:

```bash
pip install sbapp
```

The Sideband application can now be launched by running the command `sideband` in the command prompt. If needed, you can create a shortcut for Sideband on your desktop or in the start menu.

When running Sideband for the first time, a default Reticulum configuration file will be created, if you don't already have one. If you don't have any existing Reticulum connectivity available locally, you may want to edit the file, located at `C:\Users\USERNAME\.reticulum\config` and manually add an interface that provides connectivity to a wider network. If you just want to connect over the Internet, you can add one of the public hubs on the [Reticulum Testnet](https://reticulum.network/connect.html).

## Installation With pipx

You *can* use the `pipx` tool to install Sideband in an isolated environment, but on Linux you will have to launch Sideband from the command line, or create your own launcher links, since `pipx` does not support desktop integration. Unfortunately, it does not seem like `pipx` will be adding desktop integration in the near future, so restoring the original `pip` tool to its proper behaviour is recommended for now. If you want to use `pipx` anyway, it is as simple as:

```bash
# Install Sideband on Linux:
pipx install sbapp

# Install Sideband on macOS:
pipx install "sbapp[macos]"

# Optionally install Reticulum utilities:
pipx install rns

# Optionally install standalone LXMF utilities:
pipx install lxmf
```

## Example Paper Message

You can try out the paper messaging functionality by using the following QR-code. It is a paper message sent to the LXMF address `6b3362bd2c1dbf87b66a85f79a8d8c75`. To be able to decrypt and read the message, you will need to import the following base32-encoded Reticulum Identity into the app:

`3BPTDTQCRZPKJT3TXAJCMQFMOYWIM3OCLKPWMG4HCF2T4CH3YZHVNHNRDU6QAZWV2KBHMWBNT2C62TQEVC5GLFM4MN25VLZFSK3ADRQ=`

You can import the identity into Sideband in the **Encryption Keys** part of the program. After the you have imported the identity, you can scan the following QR-code and open it in the app, where it will be decrypted and added to your messages.

<p align="center"><img width="50%" src="https://raw.githubusercontent.com/markqvist/LXMF/master/docs/paper_msg_test.png"/></p>

You can also find the entire message in <a href="lxm://azNivSwdv4e2aoX3mo2MdTAozuI7BlzrLlHULmnVgpz3dNT9CMPVwgywzCJP8FVogj5j_kU7j7ywuvBNcr45kRTrd19c3iHenmnSDe4VEd6FuGsAiT0Khzl7T81YZHPTDhRNp0FdhDE9AJ7uphw7zKMyqhHHxOxqrYeBeKF66gpPxDceqjsOApvsSwggjcuHBx9OxOBy05XmnJxA1unCKgvNfOFYc1T47luxoY3c0dLOJnJPwZuFRytx2TXlQNZzOJ28yTEygIfkDqEO9mZi5lgev7XZJ0DvgioQxMIyoCm7lBUzfq66zW3SQj6vHHph7bhr36dLOCFgk4fZA6yia2MlTT9KV66Tn2l8mPNDlvuSAJhwDA_xx2PN9zKadCjo9sItkAp8r-Ss1CzoUWZUAyT1oDw7ly6RrzGBG-e3eM3CL6u1juIeFiHby7_3cON-6VTUuk4xR5nwKlFTu5vsYMVXe5H3VahiDSS4Q1aqX7I">this link</a>:

`lxm://azNivSwdv4e2aoX3mo2MdTAozuI7BlzrLlHULmnVgpz3dNT9CMPVwgywzCJP8FVogj5j_kU7j7ywuvBNcr45kRTrd19c3iHenmnSDe4VEd6FuGsAiT0Khzl7T81YZHPTDhRNp0FdhDE9AJ7uphw7zKMyqhHHxOxqrYeBeKF66gpPxDceqjsOApvsSwggjcuHBx9OxOBy05XmnJxA1unCKgvNfOFYc1T47luxoY3c0dLOJnJPwZuFRytx2TXlQNZzOJ28yTEygIfkDqEO9mZi5lgev7XZJ0DvgioQxMIyoCm7lBUzfq66zW3SQj6vHHph7bhr36dLOCFgk4fZA6yia2MlTT9KV66Tn2l8mPNDlvuSAJhwDA_xx2PN9zKadCjo9sItkAp8r-Ss1CzoUWZUAyT1oDw7ly6RrzGBG-e3eM3CL6u1juIeFiHby7_3cON-6VTUuk4xR5nwKlFTu5vsYMVXe5H3VahiDSS4Q1aqX7I`

On operating systems that allow for registering custom URI-handlers, you can click the link, and it will be decoded directly in your LXMF client. This works with Sideband on Android.

## Support Sideband Development
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

## Development Roadmap

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

## License
Unless otherwise noted, this work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

Permission is hereby granted to use Sideband in binary form, for any and all purposes, and to freely distribute binary copies of the program, so long as no payment or compensation is charged or received for such distribution or use.

<img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" align="right">

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


*Device screenshots generated with [deviceframes](https://deviceframes.com). Thanks!*
