@echo off
title 🪄 Magic Setup - One Click Installer
echo =======================================================
echo             🪄 MAGIC IMAGE TOOL SETUP
echo =======================================================
echo This will:
echo   1. Install Python (if missing)
echo   2. Install ImageMagick (if missing)
echo   3. Add this folder to your system PATH
echo   4. Make "magic" command globally available
echo =======================================================
echo.

REM Require admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Please run this script as Administrator!
    pause
    exit /b
)

REM Get current folder
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

echo 🧠 Working directory: %CURRENT_DIR%
echo.

REM -------------------------------
REM 1. Check for Python
REM -------------------------------
echo 🔍 Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 🚀 Installing latest Python...
    winget install --silent --accept-package-agreements --accept-source-agreements Python.Python.3
) else (
    for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
    echo ✅ Python %PYVER% detected.
)
echo.

REM -------------------------------
REM 2. Check for ImageMagick
REM -------------------------------
echo 🔍 Checking for ImageMagick...
magick -version >nul 2>&1
if %errorlevel% neq 0 (
    echo 🚀 Installing latest ImageMagick...
    winget install --silent --accept-package-agreements --accept-source-agreements ImageMagick.ImageMagick
) else (
    for /f "tokens=3" %%a in ('magick -version ^| find "Version"') do set IMVER=%%a
    echo ✅ ImageMagick %IMVER% detected.
)
echo.

REM -------------------------------
REM 3. Add current folder to PATH
REM -------------------------------
echo 🔧 Adding "%CURRENT_DIR%" to system PATH...

REM Get existing PATH
for /f "tokens=2* delims= " %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do setx /M PATH "%%B;%CURRENT_DIR%"

echo ✅ PATH updated successfully.
echo.

REM -------------------------------
REM 4. Verify or create magic.bat
REM -------------------------------
if not exist "%CURRENT_DIR%\magic.bat" (
    echo 📄 Creating magic.bat...
    >"%CURRENT_DIR%\magic.bat" echo @echo off
    >>"%CURRENT_DIR%\magic.bat" echo set "SCRIPT_DIR=%%~dp0"
    >>"%CURRENT_DIR%\magic.bat" echo python "%%SCRIPT_DIR%%magic.py" %%*
)
echo ✅ magic.bat ready.
echo.

REM -------------------------------
REM 5. Verify magic.py presence
REM -------------------------------
if not exist "%CURRENT_DIR%\magic.py" (
    echo ⚠️  magic.py not found in this folder!
    echo Please place your magic.py file here.
    pause
    exit /b
)
echo ✅ magic.py found.
echo.

echo =======================================================
echo ✅ Setup complete!
echo You can now use the "magic" command anywhere.
echo Example:
echo   magic 720p q80 Profile.jpg
echo =======================================================
pause
exit /b
