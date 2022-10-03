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

preparewheel:
	pyclean .
	$(MAKE) -C sbapp cleanrns

build_wheel:
	python3 setup.py sdist bdist_wheel

release: build_wheel apk fetchapk

upload:
	@echo Ready to publish release, hit enter to continue
	@read VOID
	@echo Uploading to PyPi...
	twine upload dist/sbapp-*