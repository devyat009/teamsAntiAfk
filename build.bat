@echo off
title Build Teams Anti-AFK Executable
cd /d "%~dp0"

echo ========================================================
echo        Building Teams Anti-AFK Standalone EXE
echo ========================================================
echo.

echo [1/3] Checking and installing build dependencies...
py -m pip install -r requirements.txt --quiet
py -m pip install pyinstaller --quiet

echo [2/3] Generating application icons if missing...
py -c "
import os
from PIL import Image, ImageDraw
os.makedirs('assets', exist_ok=True)
if not os.path.exists('assets/icon.ico'):
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    for s, s_h in sizes:
        img = Image.new('RGBA', (s, s_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(1, s // 16)
        draw.ellipse([margin, margin, s - margin, s_h - margin], fill=(16, 124, 65, 255), outline=(255, 255, 255, 220), width=max(1, s // 20))
        p1 = (int(s * 0.40), int(s * 0.28))
        p2 = (int(s * 0.40), int(s * 0.72))
        p3 = (int(s * 0.72), int(s * 0.50))
        draw.polygon([p1, p2, p3], fill=(255, 255, 255, 255))
        images.append(img)
    images[0].save('assets/icon.ico', format='ICO', sizes=[(img.width, img.height) for img in images], append_images=images[1:])
"

echo [3/3] Compiling standalone executable with PyInstaller...
py -m PyInstaller --onefile --noconsole --icon=assets/icon.ico --name=TeamsAntiAfk --clean main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Executable created at:
    echo  dist\TeamsAntiAfk.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed with exit code %ERRORLEVEL%.
)

pause
