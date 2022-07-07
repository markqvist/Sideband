all: prepare debug

prepare: activate cleanrns getrns

clean:
	buildozer android clean
	-(rm ./__pycache__ -r)
	-(rm ./app_storage -r)
	-(rm ./bin -r)
	
activate:
	(. venv/bin/activate)

debug:
	buildozer android debug

release:
	buildozer android release

postbuild:
	cleanrns
	@echo Done

apk: prepare release postbuild

devapk: prepare debug postbuild

install:
	adb install bin/sideband-0.1.6-arm64-v8a-release.apk

console:
	(adb logcat | grep python)

getrns:
	(cp -rv ../../Reticulum/RNS ./;rm ./RNS/Utilities/RNS;rm ./RNS/__pycache__ -r)

cleanrns:
	-(rm ./RNS -r)
