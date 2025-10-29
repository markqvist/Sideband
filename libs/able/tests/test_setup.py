from pathlib import Path
import pytest


@pytest.fixture
def parser(mocker):
    mocker.patch("setuptools.setup")
    from setup import PathParser

    return PathParser()


@pytest.mark.parametrize(
    ("cppflags", "expected"),
    [
        (
            "-I/media/able/examples/alert/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/python-installs/alert_mi/",
            "/media/able/examples/alert/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/javaclasses/alert_mi",
        ),
        (
            "-DANDROID -I/home/user/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include -I/media/able/examples/alert/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/python-installs/alert_mi/arm64-v8a/include/python3.9",
            "/media/able/examples/alert/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/javaclasses/alert_mi",
        ),
    ],
)
def test_javaclass_dir_found(mocker, parser, cppflags, expected):
    mocker.patch("os.environ", {"CPPFLAGS": cppflags})
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.mkdir")
    assert parser.javaclass_dir == Path(expected)
