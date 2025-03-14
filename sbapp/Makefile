all: prepare debug

prepare: cleanrns getrns

clean:
	@echo Cleaning...
	-(rm ./__pycache__ -r)
	-(rm ./app_storage -r)
	-(rm ./share/pkg/* -r)
	-(rm ./share/mirrors/* -rf)
	-(rm ./bin -r)

cleanlibs:
	buildozer android clean
	
cleanall: clean cleanlibs

patchfiles: patchsdl injectxml patchpycodec2

patchsdl:
	# Pach USB HID behaviour
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/build/bootstrap_builds/sdl2/jni/SDL/android-project/app/src/main/java/org/libsdl/app/HIDDeviceUSB.java
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/src/main/java/org/libsdl/app/HIDDeviceUSB.java
	cp patches/HIDDeviceUSB.java .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/jni/SDL/android-project/app/src/main/java/org/libsdl/app/HIDDeviceUSB.java

	# Pach service loader
	cp patches/PythonService.java .buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/common/build/src/main/java/org/kivy/android/PythonService.java
	cp patches/PythonService.java .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/build/bootstrap_builds/sdl2/src/main/java/org/kivy/android/PythonService.java
	cp patches/PythonService.java .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/src/main/java/org/kivy/android/PythonService.java

patchpycodec2:
	patchelf --replace-needed libcodec2.so.1.2 libcodec2.so .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/_python_bundle__arm64-v8a/_python_bundle/site-packages/pycodec2/pycodec2.so
	patchelf --replace-needed libcodec2.so.1.2 libcodec2.so .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/_python_bundle__armeabi-v7a/_python_bundle/site-packages/pycodec2/pycodec2.so

injectxml:
	# mkdir /home/markqvist/.local/lib/python3.11/site-packages/pythonforandroid/bootstraps/sdl2/build/src/main/xml
	# Inject XML on arm64-v8a
	mkdir -p .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/templates
	cp patches/AndroidManifest.tmpl.xml .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/templates/
	cp patches/p4a_build.py .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/build.py
	
debug:
	buildozer android debug

prebake:
ifneq (,$(wildcard .buildozer/android/platform/build-arm64-v8a_armeabi-v7a_x86_x86_64/dists/sideband/src/main/res/xml/device_filter.xml))
	@echo Device filter XML exists, skipping prebake
else
	@(echo Prebaking build before patching files...)
	@(sleep 2)
	(buildozer android release)  # this mustn't be ignored, or else the release will indubitably fail
	@(echo Prebake finished, applying patches and rebuilding...)
	@(sleep 2)
endif

createshare:
	# NOTICE: if the git refs of each repository here are not pinned, the build will NOT be deterministic!
	mkdir -p ../../dist_archive
	rm -vrf ../../dist_archive/*
	# mirrors
	# reticulum.network
	cp -fv ../../reticulum_website/docs/manual/Reticulum\ Manual.pdf ../../dist_archive
	cp -fv ../../reticulum_website/docs/manual/Reticulum\ Manual.epub ../../dist_archive
	-(rm -rf ../../dist_archive/reticulum.network)
	cp -frv ../../reticulum_website/docs ../../dist_archive/reticulum.network
	# unsigned.io (mirror from https://git.liberatedsystems.co.uk/jacob.eva/openCom-Companion/src/branch/master/Dockerfile)
	$(eval cwd := $(shell pwd))
	cd ../../dist_archive && \
	rm -rf ./unsigned.io && \
	wget -q https://liberatedsystems.co.uk/unsigned_io_archive.zip && \
	unzip -q unsigned_io_archive.zip && \
	rm unsigned_io_archive.zip  && \
	cd $(cwd)
	# build wheels
	# rns, rnspure, lxmf, lxst, nomadnet, rnsh
	$(eval cwd := $(shell pwd))
	cd ../../Reticulum && \
	rm -rf ./dist && \
	python3 ./setup.py bdist_wheel && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	
	$(eval cwd := $(shell pwd))
	cd ../../Reticulum && \
	rm -rf ./dist && \
	python3 ./setup.py bdist_wheel --pure && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	
	$(eval cwd := $(shell pwd))
	cd ../../LXMF && \
	rm -rf ./dist && \
	python3 ./setup.py bdist_wheel && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	
	$(eval cwd := $(shell pwd))
	cd ../../LXST && \
	rm -rf ./dist && \
	python3 ./setup.py bdist_wheel && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	
	$(eval cwd := $(shell pwd))
	cd ../../nomadnet && \
	rm -rf ./dist && \
	python3 ./setup.py bdist_wheel && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	
	$(eval cwd := $(shell pwd))
	cd ../../rnsh && \
	rm -rf ./dist && \
	poetry build && \
	cp -fv ./dist/* ../dist_archive && \
	cd $(cwd)
	# rnode firmware source zip
	cd ../../dist_archive && \
	curl -L https://github.com/markqvist/RNode_Firmware/archive/refs/heads/master.zip --clobber -o RNode_Firmware-master.zip && \
	cd $(cwd)

fetchshare:
	mkdir -p ./share/pkg
	-(rm ./share/pkg/*)
	mkdir -p ./share/mirrors
	-(rm ./share/mirrors/* -r)
	cp -fv ../../dist_archive/rns-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/rnspure-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/lxmf-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/lxst-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/nomadnet-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/rnsh-*-py3-none-any.whl ./share/pkg/
	cp -fv ../../dist_archive/RNode_Firmware-*.zip ./share/pkg/
	zip --junk-paths ./share/pkg/example_plugins.zip ../docs/example_plugins/*.py
	cp -rfv ../../dist_archive/reticulum.network ./share/mirrors/
	cp -rfv ../../dist_archive/unsigned.io ./share/mirrors/
	cp -fv ../../dist_archive/Reticulum\ Manual.pdf ./share/mirrors/Reticulum_Manual.pdf
	cp -fv ../../dist_archive/Reticulum\ Manual.epub ./share/mirrors/Reticulum_Manual.epub
	cp -rfv ../../rnode-flasher ./share/mirrors/
	-(rm ./share/mirrors/rnode-flasher/.git -rf)

release:
	buildozer android release

postbuild:
	$(MAKE) cleanrns

apk: clean prepare prebake patchfiles createshare fetchshare release postbuild

devapk: clean prepare prebake patchfiles debug postbuild

version:
	@(echo $$(python ./gv.py))

install:
	adb install -r bin/sideband-$$(python ./gv.py)-arm64-v8a_armeabi-v7a_x86_x86_64-release.apk

devinstall:
	adb install -r bin/sideband-$$(python ./gv.py)-arm64-v8a_armeabi-v7a_x86_x86_64-debug.apk

install-multi:
	adb devices | tail -n +2 | cut -sf 1 | xargs -iX adb -s X install -r ./bin/sideband-$$(python ./gv.py)-arm64-v8a_armeabi-v7a_x86_x86_64-release.apk

devinstall-multi:
	adb devices | tail -n +2 | cut -sf 1 | xargs -iX adb -s X install -r ./bin/sideband-$$(python ./gv.py)-arm64-v8a_armeabi-v7a_x86_x86_64-debug.apk

console:
	(adb logcat | grep "python\|sidebandservice")

getrns:
	(cp -rv ../../Reticulum/RNS ./)
	-(rm ./RNS/Utilities/RNS) # created by the create_symlinks target in Reticulum
	-(rm ./RNS/__pycache__ -r)
	(cp -rv ../../LXMF/LXMF ./)
	-(rm ./LXMF/Utilities/LXMF) # ditto
	-(rm ./LXMF/__pycache__ -r)
	(cp -rv ../../LXST/LXST ./)
	-(rm ./LXST/Utilities/LXST)
	-(rm ./LXST/__pycache__ -r)
	-(rm ./LXST/Utilities/__pycache__ -r)

cleanrns:
	-(rm ./RNS -r)
	-(rm ./LXMF -r)
