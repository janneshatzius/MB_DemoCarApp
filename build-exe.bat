@echo off
rmdir /s /q dist build
del /q *.spec

pyinstaller --noconfirm --clean --windowed --name MB_DemoCarApp --add-data "assets;assets" --icon "assets\App-Logo.ico" presentation\main_app.py

pause
