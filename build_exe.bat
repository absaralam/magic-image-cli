@echo off
setlocal EnableExtensions DisableDelayedExpansion

title 🏗️ Building Magic Executable

echo =======================================================
echo             🏗️ MAGIC BUILD SYSTEM
echo =======================================================
echo.

:: 1. Check/Install PyInstaller
echo 🔍 Checking for PyInstaller...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo ✅ PyInstaller is ready.
)
echo.

:: 2. Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "magic.spec" del "magic.spec"

:: 3. Build the Exe
echo 🔨 Compiling magic.py...
echo    This may take a minute...
python -m PyInstaller --noconfirm --onefile --console --name "magic" --clean "magic.py"

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo =======================================================
echo ✅ Build Complete!
echo 📂 Executable is in: dist\magic.exe
echo =======================================================

:: 4. Auto-update version.txt
echo 🔄 Syncing version.txt...
(
echo import re
echo with open('magic.py', 'r') as f:
echo     content = f.read(^)
echo     match = re.search(r'__version__\s*=\s*"([^"]+)"', content^)
echo     if match: print(match.group(1^)^)
) > get_version.py

python get_version.py > version.txt
del get_version.py

set /p VER=<version.txt
echo 🏷️  Version set to: %VER%
echo.

pause
