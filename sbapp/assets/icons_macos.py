import sys
import pathlib
import argparse
import subprocess
import platform

__version_info__ = (1, 2, 0)
__version__ = ".".join(map(str, __version_info__))

__copyright__: str = f"Copyright (C) 2018-2022 Declaration of VAR"

# default iconset files extension, gets the value from original image
ext = ".png"
# programs names
iconutilProgram = "iconutil"
magickProgram = "magick"
sipsProgram = "sips"


class IconParameters():
    width = 0
    scale = 1

    def __init__(self, width, scale):
        self.width = width
        self.scale = scale

    def getIconName(self):
        global ext
        scaleString = "" if self.scale == 1 else f"@{self.scale}x"
        return f"icon_{self.width}x{self.width}{scaleString}{ext}"


def checkProgramInPath(programName, errorMsg=None):
    checkResult = subprocess.run(
        ["which", programName],
        capture_output=True,
        text=True
    )
    errorMsgString = "" if errorMsg is None else f". {errorMsg}"
    if checkResult.returncode != 0:
        raise SystemExit(
            f"[ERROR] Couldn't find {programName} in your PATH{errorMsgString}"
        )
    else:
        print(f"Found {programName}: {checkResult.stdout.strip()}")


def generateImageConvertingCommand(forSips, originalPicture, ip, iconsetDir):
    if not forSips:
        return [
            magickProgram,
            "convert",
            originalPicture,
            "-resize",
            str(ip.width * ip.scale),
            iconsetDir / ip.getIconName()
        ]
    else:
        return [
            sipsProgram,
            "-z",
            str(ip.width * ip.scale),
            str(ip.width * ip.scale),
            originalPicture,
            "--out",
            iconsetDir / ip.getIconName()
        ]


def main():
    global ext

    argParser = argparse.ArgumentParser(
        prog="generate-iconset",
        description=" ".join((
            f"%(prog)s\n{__copyright__}\nGenerate",
            "an iconset for a Mac OS application",
            f"using {iconutilProgram} tool"
        )),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False
    )
    argParser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    argParser.add_argument(
        "image",
        metavar="/path/image.png",
        help="path to the original image"
    )
    argParser.add_argument(
        "--out",
        metavar="/path/out/",
        help=" ".join((
            "path to the output folder, where to put resulting",
            ".icns file (default: same folder as original image)"
        ))
    )
    argParser.add_argument(
        "--use-sips",
        action='store_true',
        help=f"use {sipsProgram} instead of ImageMagick (default: %(default)s)"
    )
    argParser.add_argument(
        "--force-png",
        action='store_true',
        help=" ".join((
            "force non-.png original image to be converted",
            "to .png (default: %(default)s)"
        ))
    )
    argParser.add_argument(
        "--ignore-non-mac",
        action='store_true',
        help=" ".join((
            "allows to run the script on any OS, not only on Mac OS",
            "(default: %(default)s)"
        ))
    )
    # argParser.add_argument(
    #     "--delete-tmp-iconset",
    #     action='store_true',
    #     help=" ".join((
    #         "delete temporary iconset directory,",
    #         "if it already exists (default: %(default)s)"
    #     ))
    # )
    cliArgs = argParser.parse_args()
    # print(cliArgs)

    if platform.system() != "Darwin":
        if not cliArgs.ignore_non_mac:
            raise SystemExit(
                " ".join((
                    "[ERROR] The script is meant to be executed",
                    f"on Mac OS only, as {iconutilProgram} tool is only available",
                    "there. You can ignore this condition",
                    "with --ignore-non-mac"
                ))
            )
        else:
            print(
                " ".join((
                    "[WARNING] You are running the script not on Mac OS,",
                    "so it is likely to fail,",
                    f"unless you have {iconutilProgram} tool installed"
                ))
            )

    checkProgramInPath(iconutilProgram)

    if not cliArgs.use_sips:
        print("Will use ImageMagick for converting the original image")
        checkProgramInPath(
            magickProgram,
            " ".join((
                "Perhaps, you don't have it installed?",
                f"You can also use {sipsProgram} tool instead",
                "with --use-sips"
            ))
        )
    else:
        print(f"Will use {sipsProgram} for converting the original image")
        print(
            " ".join((
                "[WARNING] ImageMagick provides better quality results,",
                f"so do consider using it instead of {sipsProgram}. More details:",
                "https://decovar.dev/blog/2019/12/12/imagemagick-vs-sips-resize/"
            ))
        )
        checkProgramInPath(sipsProgram)

    print()

    originalPicture = pathlib.Path(cliArgs.image)
    if not (originalPicture.is_file()):
        raise SystemExit(
            f"[ERROR] There is no such image file: {cliArgs.image}"
        )
    print(f"Original image: {originalPicture}")

    fname = pathlib.Path(originalPicture).stem
    ext = pathlib.Path(originalPicture).suffix
    if ext != ".png":
        if not cliArgs.force_png:
            print(
                " ".join((
                    "[WARNING] Original image extension is not .png,",
                    f"{iconutilProgram} is likely to fail,",
                    "pass --force-png to avoid that"
                ))
            )
        else:
            ext = ".png"

    # destination path for output
    destDir = (
        pathlib.Path(originalPicture).parent
        if cliArgs.out is None
        else pathlib.Path(cliArgs.out)
    )
    if not (destDir.is_dir()):
        try:
            destDir.mkdir(parents=True)
        except Exception as ex:
            raise SystemExit(
                " ".join((
                    "[ERROR] The specified output folder doesn't exist",
                    f"and could not be created: {cliArgs.out}"
                ))
            )
    # path to resulting .icns file
    resultingIconset = destDir / f"{fname}.icns"

    # path to temporary iconset folder
    iconsetDir = pathlib.Path(destDir / f"{fname}.iconset")
    if not (iconsetDir.is_dir()):
        try:
            iconsetDir.mkdir()
        except Exception as ex:
            raise SystemExit(
                " ".join((
                    "[ERROR] Could not create temporary",
                    f"iconset folder: {iconsetDir}"
                ))
            )
    else:
        if False:  # cliArgs.delete_tmp_iconset:
            # not the best idea to let script delete files on disk
            print("[DEBUG] Deleting temporary iconset folder")
        else:
            raise SystemExit(
                " ".join((
                    f"[ERROR] Temporary iconset directory ({iconsetDir})",
                    "already exists, you need to",
                    "delete it first"
                    # "either delete it manually",
                    # "or use --delete-tmp-iconset"
                ))
            )

    # https://developer.apple.com/design/human-interface-guidelines/macos/icons-and-images/app-icon#app-icon-sizes
    ListOfIconParameters = [
        IconParameters(16, 1),
        IconParameters(16, 2),
        IconParameters(32, 1),
        IconParameters(32, 2),
        IconParameters(128, 1),
        IconParameters(128, 2),
        IconParameters(256, 1),
        IconParameters(256, 2),
        IconParameters(512, 1),
        IconParameters(512, 2)
    ]

    print("Converting images for iconset")

    # generate iconset
    currentImage = 0
    for ip in ListOfIconParameters:
        currentImage += 1
        convertingResult = subprocess.run(
            generateImageConvertingCommand(
                cliArgs.use_sips,
                originalPicture,
                ip,
                iconsetDir
            ),
            capture_output=True,
            text=True
        )
        if convertingResult.returncode != 0:
            raise SystemExit(
                f"[ERROR] Conversion failed. {convertingResult.stderr.strip()}"
            )
        else:
            print(f"{currentImage}/{len(ListOfIconParameters)}...")
        # print(f"Generated {ip.getIconName()}")

    print("\nGenerating .icns file...")
    # convert iconset folder to .icns file
    iconutilResult = subprocess.run(
        [
            iconutilProgram,
            "-c",
            "icns",
            iconsetDir,
            "-o",
            resultingIconset
        ],
        capture_output=True,
        text=True
    )
    if iconutilResult.returncode != 0:
        raise SystemExit(
            " ".join((
                f"[ERROR] {iconutilProgram} could not generate",
                f"an iconset. {iconutilResult.stderr.strip()}"
            ))
        )
    else:
        print(
            " ".join((
                "[SUCCESS] An iconset was successfully",
                f"generated to {resultingIconset}"
            ))
        )
        raise SystemExit(0)


if __name__ == '__main__':
    main()
