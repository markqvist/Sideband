### Establishing a Development environment

Looking to contribute some code to Sideband? Awesome! Follow the guide below to get the repository building on your machine.

#### Required dependencies for development

Until this repository has a `flake.nix` added, you will need to manually download the following dependencies using your Operating System's package manager.

- `make`
- `adb` (available as a part of the `android-tools` package on Fedora, `adb` on Debian/Ubuntu, `android-platform-tools` on Brew Casks)
- `python3`/`python3-dev(el)` (must be available as `python`)
- `patchelf`
- `patch`
- `perl`
- `buildozer` (see https://buildozer.readthedocs.io/en/latest/installation.html)
    - buildozer's PyPI hosted version is very far behind, therefore you should install from source at https://github.com/kivy/buildozer.git; this is easy with pipx `pipx install git+https://github.com/kivy/buildozer.git`.
    - buildozer needs `wheel` to run, but it is not currently marked as a dependency. If you are using pipx, you will need to inject it with `pipx inject wheel`.
- all of buildozer's Android dependencies (at the time of writing, the Debian packages `git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev`) (Fedora/RHEL equivalents `git zip unzip java-17-openjdk java-17-openjdk-devel python3-pip autoconf libtool pkgconf-pkg-config ghc-zlib-devel ncurses-devel ncurses-compat-libs cmake libffi-devel openssl-devel`)

In the root directory of the repository, use `pip install .` to install the package from `setup.py`. The use of a `venv` is strongly recommended.

Make sure you manually install `Cython<3.0` into your Python install or `venv`, as buildozer will need it for Android.

#### Creating folders

Sideband relies on a certain folder structure to achieve a psuedo-monorepo structure with the other Reticulum projects.

To make sure that the `getrns` target runs successfully, make sure your directory tree looks like this:

```
repositories/
├─ LXMF/
├─ dist_archive/
├─ rnode-flasher/
└─ Reticulum/
```

LXMF can be obtained from https://github.com/markqvist/LXMF, Reticulum from https://github.com/markqvist/Reticulum, and rnode-flasher from https://github.com/liamcottle/rnode-flasher.

`dist_archive` can simply be an empty folder. It is used by Sideband for the built-in repository server, but not necessary for development.

#### Creating and testing Sideband on an Android device

With a correctly configured environment, run the following command to create a development APK.

```
make devapk
```

If you would like your release to be signed, you must configure the following four environment variables:

- `P4A_RELEASE_KEYALIAS`
- `P4A_RELEASE_KEYSTORE_PASSWD`
- `P4A_RELEASE_KEYSTORE`
- `P4A_RELEASE_KEYALIAS_PASSWD`

If you would like to build a distribution-ready release, you must also configure the `dist_archive`.

Please contact [`@unsignedmark:matrix.org`](https://matrix.to/#/@unsignedmark:matrix.org) for help doing this.

After it is configured correctly, you may build it with

```
make apk
```

Regardless of what release type you build, the output will be placed in `./sbapp/bin/`.

#### Addendum: Fedora

As many users of Kivy have noted before, some of Python4Android's recipies do not compile correctly on Fedora/RHEL. For this project, one package of interest is [`freetype-py` and its native dependency](https://github.com/kivy/python-for-android/blob/develop/pythonforandroid/recipes/freetype/__init__.py), which is a direct dependency of pillow, the ubiquitous Python image editing library.

The use of Ubuntu is therefore recommended for developing this project. Sideband does run fine on Fedora, however.
