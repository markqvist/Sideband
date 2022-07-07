devapk:
    make -C sbapp devapk

apk:
    make -C sbapp apk

install:
    make -C sbapp install

console:
    make -C sbapp conole

clean:
    @echo Cleaning...
    -rm -r ./build
    -rm -r ./dist

build_wheel:
    python3 setup.py sdist bdist_wheel

release: build_wheel apk