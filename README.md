Sideband <img align="right" src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg"/>
=========

Sideband is an LXMF client for Android, Linux and macOS. It allows you to communicate with other people or LXMF-compatible systems over Reticulum networks using LoRa, Packet Radio, WiFi, I2P, or anything else Reticulum supports.

![Screenshot](https://github.com/markqvist/Sideband/raw/main/docs/screenshots/devices_small.webp)

Sideband is completely free, end-to-end encrypted, permission-less, anonymous and infrastructure-less. Sideband uses the peer-to-peer and distributed messaging system [LXMF](https://github.com/markqvist/lxmf "LXMF"). There is no sign-up, no service providers, no "end-user license agreements", no data theft and no surveillance. You own the system.

This also means that Sideband operates differently than what you might be used to. It does not need a connection to a server on the Internet to function, and you do not have an account anywhere. Please read the Guide section included in the program, to get an understanding of how Sideband differs from other messaging systems.

The program currently includes basic functionality for secure and independent communication, and many useful features are planned for implementation. Sideband is currently released as a beta version. Please help make all the functionality a reality by supporting the development with donations.

Sideband works well with the terminal-based LXMF client [Nomad Network](https://github.com/markqvist/nomadnet), which allows you to easily host Propagation Nodes for your LXMF network, and more.

If you want to help develop this program, get in touch.

## Installation

For your Android devices, download an [APK on the latest release](https://github.com/markqvist/Sideband/releases/latest) page. If you prefer to install via F-Droid, you can add the [IzzyOnDroid Repository](https://android.izzysoft.de/repo/info) to your F-Droid client, which includes Sideband.

A DMG file containing a macOS app bundle is also available on the  [latest release](https://github.com/markqvist/Sideband/releases/latest) page.

Aditionally, you can install Sideband with ``pip`` on Linux and macOS:

```bash
# Install Sideband and dependencies on Linux
pip install sbapp

# Install Sideband and dependencies on macOS
pip install "sbapp[macos]"

# Run it
sideband

```

## Support Sideband Development
You can help support the continued development of open, free and private communications systems by donating via one of the following channels:

- Monero:
  ```
  84FpY1QbxHcgdseePYNmhTHcrgMX4nFfBYtz2GKYToqHVVhJp8Eaw1Z1EedRnKD19b3B8NiLCGVxzKV17UMmmeEsCrPyA5w
  ```
- Ethereum
  ```
  0x81F7B979fEa6134bA9FD5c701b3501A2e61E897a
  ```
- Bitcoin
  ```
  3CPmacGm34qYvR6XWLVEJmi2aNe3PZqUuq
  ```
- Ko-Fi: https://ko-fi.com/markqvist

<br/>

## Development Roadmap

- Adding a Nomad Net page browser
- Implementing the Local Broadcasts feature
- Adding a debug log option and viewer
- Adding a Linux .desktop file
- Message sorting mechanism
- Fix I2P status not being displayed correctly when the I2P router disappears unexpectedly
- Adding LXMF sneakernet and paper message functionality

## License
Unless otherwise noted, this work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

Permission is hereby granted to use Sideband in binary form, for any and all purposes, and to freely distribute binary copies of the program, so long as no payment or compensation is charged or received for such distribution or use.

<img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" align="right">

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


*Device screenshots generated with [deviceframes](https://deviceframes.com). Thanks!*
