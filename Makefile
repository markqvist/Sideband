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

build_wheel: remove_symlinks compile_wheel create_symlinks

build_win_exe:
	python -m PyInstaller sideband.spec --noconfirm

release: build_wheel apk fetchapk

upload:
	@echo Ready to publish release, hit enter to continue
	@read VOID
	@echo Uploading to PyPi...
	twine upload dist/sbapp-*