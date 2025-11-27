include environment

devapk:
	make -C sbapp devapk

apk:
	make -C sbapp apk
	mkdir -p ./dist

fetchapk:
	cp ./sbapp/bin/sideband-*-release.apk ./dist/

install:
	make -C sbapp install

console:
	make -C sbapp console

clean:
	@echo Cleaning...
	-rm -r ./build
	-rm -r ./dist

cleanbuildozer:
	make -C sbapp cleanall

cleanall: clean cleanbuildozer

remove_symlinks:
	@echo Removing symlinks for build...
	-rm ./RNS
	-rm ./LXST
	-rm ./LXMF

create_symlinks:
	@echo Creating symlinks...
	-ln -s ../Reticulum/RNS ./RNS
	-ln -s ../LXST/LXST ./LXST
	-ln -s ../LXMF/LXMF ./LXMF

preparewheel:
	pyclean .
	$(MAKE) -C sbapp cleanrns

compile_wheel:
	python3 setup.py bdist_wheel

compile_sourcepkg:
	python3 setup.py sdist

update_share:
	$(MAKE) -C sbapp fetchshare

build_wheel: remove_symlinks update_share compile_wheel create_symlinks

build_spkg: remove_symlinks update_share compile_sourcepkg create_symlinks

prepare_win_pkg: clean build_spkg
	-rm -r build/winpkg
	mkdir -p build/winpkg
	LC_ALL=C $(MAKE) -C ../Reticulum clean build_spkg
	cp ../Reticulum/dist/rns-*.*.*.tar.gz build/winpkg
	cd build/winpkg; tar -zxf rns-*.*.*.tar.gz
	mv build/winpkg/rns-*.*.*/RNS build/winpkg; rm -r build/winpkg/rns-*.*.*
	LC_ALL=C $(MAKE) -C ../LXMF clean build_spkg
	cp ../LXMF/dist/lxmf-*.*.*.tar.gz build/winpkg
	cd build/winpkg; tar -zxf lxmf-*.*.*.tar.gz
	mv build/winpkg/lxmf-*.*.*/LXMF build/winpkg; rm -r build/winpkg/lxmf-*.*.*
	LC_ALL=C $(MAKE) -C ../LXST clean build_spkg
	cp ../LXST/dist/lxst-*.*.*.tar.gz build/winpkg
	cd build/winpkg; tar -zxf lxst-*.*.*.tar.gz
	mv build/winpkg/lxst-*.*.*/LXST build/winpkg; rm -r build/winpkg/lxst-*.*.*
	rm build/winpkg/LXST/filterlib*.so
	cp dist/sbapp-*.*.*.tar.gz build/winpkg
	cd build/winpkg; tar -zxf sbapp-*.*.*.tar.gz
	mv build/winpkg/sbapp-*.*.*/* build/winpkg; rm -r build/winpkg/sbapp-*.*.*
	rm build/winpkg/LXST/Codecs/libs/pyogg/libs/macos -r
	cp winbuild.bat winbuild.ps1 build/
	mv build/winpkg build/sideband_sources
	cd build; zip -r winbuild.zip sideband_sources winbuild.bat winbuild.ps1
	mv build/winbuild.zip dist/winbuild.zip

build_winexe: prepare_win_pkg
	cp dist/winbuild.zip $(WINDOWS_BUILD_TARGET)

release: build_wheel apk fetchapk

upload:
	@echo Ready to publish release, hit enter to continue
	@read VOID
	@echo Uploading to PyPi...
	twine upload dist/sbapp-*
