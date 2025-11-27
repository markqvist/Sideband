@echo off
cd sideband_sources\sbapp
for /f "delims=" %%v in ('powershell.exe -Command "python gv.py"') do set version=%%v
cd ..\..
echo Compiling Sideband %version%

cd sideband_sources
python -m PyInstaller sideband.spec --noconfirm
cd ..

set "source_dir=Sideband_%version%"
set "zip_file=Sideband_%version%.zip"
move sideband_sources\dist\main %source_dir%
powershell.exe -Command "Compress-Archive -Path '%source_dir%' -DestinationPath '%zip_file%' -Force"

echo Build completed