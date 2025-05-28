@echo off
REM — clean previous builds
rmdir /s /q dist build
del /q *.spec

REM — build the GUI app in one-folder mode
pyinstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name DemoCarApp ^
  --paths . ^
  --add-data "assets;assets" ^
  --icon "assets\App-Logo.ico" ^
  "presentation\main_app.py"

pause

