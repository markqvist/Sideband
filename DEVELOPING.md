# Establishing a Development environment

Looking to contribute some code to Sideband? Awesome! Follow the guide below to get the repository building on your machine.

## Creating folders

Sideband relies on a certain folder structure to achieve a psuedo-monorepo structure with the other Reticulum projects.

To make sure that the `getrns` target runs successfully, make sure your directory tree looks like this:

```
repositories/
├─ LXMF/
├─ LXST/
├─ rnsh/
├─ rnode-flasher/
├─ Reticulum/
├─ NomadNet/
├─ reticulum_website/
└─ Sideband/
```

Below are the git repositories for some of the above folders:

- `LXMF`: https://github.com/markqvist/LXMF
- `LXST`: https://github.com/markqvist/LXST
- `rnsh`: https://github.com/acehoss/rnsh
- `Reticulum`: https://github.com/markqvist/Reticulum
- `rnode-flasher`: https://github.com/liamcottle/rnode-flasher
- `NomadNet`: https://github.com/markqvist/nomadnet
- `reticulum_website`: https://github.com/markqvist/reticulum_website

> Please note: in order for the docker script and `createshare` make target to work correctly, your directory **must** be laid out like this.

## Required dependencies for development (Docker)

If you have a Fedora-based Linux system (see [Addendum: Fedora](#addendum-fedora)) or simply would not like to install all of P4A's dependencies manually, you may choose to use the containerized build.

This method requires that you have Docker installed on your system: https://docs.docker.com/engine/install/

Additionally, [rootless Docker](https://docs.docker.com/engine/install/) should be used to minimize any possible attack surface on your system. Never run a script you haven't vetted with sudo! The `./dmake.sh` script uses `set -ex` and is designed to be used with rootless docker.

After configuring docker, you can replace any use of the `make` command with `dmake` (i.e. `./dmake devapk`) to run make commands in the container, building it on demand if needed. 

Example:

```
./dmake devapk
```

(or if running in sbapp, it is smart enough to run itself in Sideband regardless of where it is called from)

```
../dmake devapk
```

## Required dependencies for development (Native)

Until this repository has a `flake.nix` added, you will need to manually download the following dependencies using your Operating System's package manager.

- `make`
- `adb` (available as a part of the `android-tools` package on Fedora, `adb` on Debian/Ubuntu, `android-platform-tools` on Brew Casks)
- `python3`/`python3-dev(el)` (must be available as `python`, on Ubuntu try `apt install python-is-python3`)
- `patchelf`
- `patch`
- `perl`
- `portaudio19-dev`
- `libopus-dev`
- `libogg-dev`
- `buildozer` (see https://buildozer.readthedocs.io/en/latest/installation.html)
    - buildozer's PyPI hosted version is very far behind, therefore you should install from source at https://github.com/kivy/buildozer.git; this is easy with pipx `pipx install git+https://github.com/kivy/buildozer.git`.
    - buildozer needs `wheel` to run, but it is not currently marked as a dependency. If you are using pipx, you will need to inject it with `pipx inject buildozer wheel`.
- all of buildozer's Android dependencies
  - Ubuntu 22.04 LTS packages `git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev`
  - Ubuntu 24.04 LTS packages `git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses-dev libtinfo6 cmake libffi-dev libssl-dev`
  - Fedora 41 `git zip unzip java-17-openjdk java-17-openjdk-devel python3-pip autoconf libtool pkgconf-pkg-config ghc-zlib-devel ncurses-devel ncurses-compat-libs cmake libffi-devel openssl-devel`

In the root directory of the repository, use `pip install .` to install the package from `setup.py`. The use of a `venv` is strongly recommended.

Make sure you manually install `Cython<3.0` into your Python install or `venv`, as buildozer will need it for Android.

### Addendum: Fedora

As many users of Kivy have noted before, some of Python4Android's recipes do not compile correctly on Fedora/RHEL. For this project, one package of interest is [`freetype-py` and its native dependency](https://github.com/kivy/python-for-android/blob/develop/pythonforandroid/recipes/freetype/__init__.py), which is a direct dependency of pillow, the ubiquitous Python image editing library.

This is due to the fact that Fedora and several other distros include default versions of toolchains, which prompts python4android to abstain from downloading its own. [This issue has been encountered by many other users.](https://groups.google.com/g/kivy-users/c/z46lSJXgbjY/m/M1UoWwtWAgAJ)

If you can't use Docker, use of Ubuntu 24.04 LTS is therefore recommended for developing this project. Ubuntu 22.04 LTS is not supported, as its `cmake` version (even with backports) is below the minimum 3.24.

Sideband does run fine on Fedora, however.

## Compiling and testing Sideband on an Android device

With a correctly configured environment, run the following command to create a development APK.

```
make devapk
```

You can then install it to a connected device with

```
make devinstall
```

If you would like your release to be signed for release, you must configure the following four environment variables:

- `P4A_RELEASE_KEYALIAS`
- `P4A_RELEASE_KEYSTORE_PASSWD`
- `P4A_RELEASE_KEYSTORE`
- `P4A_RELEASE_KEYALIAS_PASSWD`

With `./dmake`, omitting any of these values will cause it to default to the `debug.keystore` generated with each install of the Android SDK.

After it is configured correctly, you may build it with

```
make apk
```

and install it to a connected device with

```
make install
```

The output will be placed in `./sbapp/bin/sideband-*.apk`.

If you have multiple devices connected at once (for example, while developing the BLE interface between devices), you may use `devinstall-multi` or `install-multi` in place of `devinstall` and `install` respectively.

If using an Android that provides the ability to toggle DCL via storage (like GrapheneOS), make sure to enable it for Sideband, as it must load its Cython executables.

## Compiling and testing Sideband for other platforms

For Windows, use the following command: (make sure you have `PyInstaller` in your venv, and you are on Windows, as PyInstaller removed cross-compilation)

```
make build_win_exe
```

Wheels for other platforms can be built with 

```
make build_wheel
```
