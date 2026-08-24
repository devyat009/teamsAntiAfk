@echo off
title Teams Anti-AFK
cd /d "%~dp0"

echo [Teams Anti-AFK] Checking dependencies...
py -m pip install -r requirements.txt --quiet

echo [Teams Anti-AFK] Starting System Tray Application...
echo Hotkey: Win + Ctrl + Shift + F (Stop / Resume)
echo Idle threshold: 4 minutes
py main.py
pause
