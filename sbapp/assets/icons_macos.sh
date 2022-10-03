#!/bin/bash
rm icon.icns
rm -r icon.iconset
python3 icons_macos.py icon_macos.png --out ./ --use-sips
mv icon_macos.icns icon.icns
mv icon_macos.iconset icon.iconset
