@echo off
REM
rmdir /s /q dist build
del /q *.spec

REM 
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

