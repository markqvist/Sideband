[app]
title = Sideband
package.name = sideband
package.domain = io.unsigned

source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,ttf,kv,pyi,typed,so,0,1,2,3,atlas,frag,html,css,js,whl,zip,gz,woff2,pdf,epub,pgm
source.include_patterns = assets/*,assets/fonts/*,share/*
source.exclude_patterns = app_storage/*,venv/*,Makefile,./Makefil*,requirements,precompiled/*,parked/*,./setup.py,Makef*,./Makefile,Makefile

version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py
android.numeric_version = 20240531

# Cryptography recipe is currently broken, using RNS-internal crypto for now. Since
# relevant PRs have now been merged in Kivy/P4A, the next release will hopefully allow
# building a non-ancient PyCa/Cryptography distribution again. When this happens, add
# the "cryptography" dependency back in here.
requirements = kivy==2.3.0,libbz2,pillow==10.2.0,qrcode==7.3.1,usb4a,usbserial4a,libwebp,libogg,libopus,opusfile,numpy,cryptography,pydub,ffpyplayer

android.gradle_dependencies =  com.android.support:support-compat:28.0.0
#android.enable_androidx = True
#android.add_aars = patches/support-compat-28.0.0.aar

p4a.local_recipes = ../recipes/

icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash_small.png
android.presplash_color = #00000000

# TODO: Fix
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,POST_NOTIFICATIONS,WAKE_LOCK,FOREGROUND_SERVICE,CHANGE_WIFI_MULTICAST_STATE,BLUETOOTH_CONNECT,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,MANAGE_EXTERNAL_STORAGE,ACCESS_BACKGROUND_LOCATION,RECORD_AUDIO

android.api = 31
android.minapi = 24
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True
android.release_artifact = apk
android.archs = arm64-v8a,armeabi-v7a
#android.logcat_filters = *:S python:D

services = sidebandservice:services/sidebandservice.py:foreground
android.whitelist = lib-dynload/termios.so
android.manifest.intent_filters = patches/intent-filter.xml

[buildozer]
log_level = 2
warn_on_root = 0
build_dir = ./.buildozer
bin_dir = ./bin
