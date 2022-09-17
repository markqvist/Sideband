all: prepare debug

prepare: activate cleanrns getrns

clean:
	-(rm ./__pycache__ -r)
	-(rm ./app_storage -r)
	-(rm ./bin -r)

cleanlibs:
	buildozer android clean
	
cleanall: clean cleanlibs

activate:
	(. venv/bin/activate)

pacthfiles: patchsdl injectxml

patchsdl:
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a/build/bootstrap_builds/sdl2/jni/SDL/android-project/app/src/main/java/org/libsdl/app/HIDDeviceUSB.java
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a/dists/sideband/src/main/java/org/libsdl/app/HIDDeviceUSB.java
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a/dists/sideband/jni/SDL/android-project/app/src/main/java/org/libsdl/app/HIDDeviceUSB.java

injectxml:
	mkdir -p .buildozer/android/platform/build-arm64-v8a/dists/sideband/src/main/res/xml
	mkdir -p .buildozer/android/platform/build-arm64-v8a/dists/sideband/templates
	cp patches/device_filter.xml .buildozer/android/platform/build-arm64-v8a/dists/sideband/src/main/res/xml/
	cp patches/AndroidManifest.tmpl.xml .buildozer/android/platform/build-arm64-v8a/dists/sideband/templates/

debug:
	buildozer android debug

prebake:
	-(buildozer android release)
	@(echo Prebake finished, applying patches and rebuilding...)
	-(sleep 2)

release:
	buildozer android release

postbuild: cleanrns

apk: prepare prebake pacthfiles release postbuild

devapk: prepare prebake pacthfiles debug postbuild

version:
	@(echo $$(python ./gv.py))

install:
	adb install bin/sideband-$$(python ./gv.py)-arm64-v8a-release.apk

console:
	(adb logcat | grep python)

getrns:
	(cp -rv ../../Reticulum/RNS ./;rm ./RNS/Utilities/RNS;rm ./RNS/__pycache__ -r)

cleanrns:
	-(rm ./RNS -r)
