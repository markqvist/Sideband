all: prepare debug

prepare: activate

clean:
	buildozer android clean
	
activate:
	(. venv/bin/activate)
	(mv setup.py setup.disabled)

debug:
	buildozer android debug

release:
	buildozer android release

postbuild:
	(mv setup.disabled setup.py)

apk: prepare release postbuild

devapk: prepare debug postbuild

install:
	adb install bin/sideband-0.1.5-arm64-v8a-debug.apk

install-release:
	adb install bin/sideband-0.1.5-arm64-v8a-release.apk

console:
	(adb logcat | grep python)

getrns:
	(rm ./RNS -r;cp -rv ../Reticulum/RNS ./;rm ./RNS/Utilities/RNS;rm ./RNS/__pycache__ -r)
