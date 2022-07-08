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

debug:
	buildozer android debug

release:
	buildozer android release

postbuild: cleanrns

apk: prepare release postbuild

devapk: prepare debug postbuild

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
