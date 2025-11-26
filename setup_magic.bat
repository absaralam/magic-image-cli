@echo off
setlocal EnableExtensions DisableDelayedExpansion

:: ===========================================================================
::  Script: setup_magic.bat
::  Description: One-click installer for the Magick Image CLI.
::               Installs Python, ImageMagick, and dependencies.
::               Sets up the system PATH and creates the magic.bat wrapper.
:: ===========================================================================

title 🪄 Magic Setup - One Click Installer

echo =======================================================
echo             🪄 MAGIC IMAGE TOOL SETUP
echo =======================================================
echo This will:
echo   1. Install Python (if missing)
echo   2. Install ImageMagick (if missing)
echo   3. Install Python Dependencies (Pillow, Watchdog, etc.)
echo   4. Add this folder to your system PATH
echo   5. Create/Restore the "magic.bat" wrapper
echo =======================================================
echo.

:: ---------------------------------------------------------------------------
::  1. Admin Check
:: ---------------------------------------------------------------------------

net session >nul 2>&1
if errorlevel 1 goto :ErrorNoAdmin

:: Get current folder (remove trailing backslash)
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

echo 🧠 Working directory: %CURRENT_DIR%
echo.

:: ---------------------------------------------------------------------------
::  2. Python Installation
:: ---------------------------------------------------------------------------

echo 🔍 Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 🚀 Installing latest Python...
    winget install --silent --accept-package-agreements --accept-source-agreements Python.Python.3
    if errorlevel 1 goto :ErrorInstallPython
) else (
    echo ✅ Python detected.
)
echo.

:: ---------------------------------------------------------------------------
::  3. Dependencies
:: ---------------------------------------------------------------------------

echo 📦 Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r "%CURRENT_DIR%\requirements.txt"
if errorlevel 1 goto :ErrorInstallDeps

echo ✅ Dependencies installed.
echo.

:: ---------------------------------------------------------------------------
::  4. ImageMagick Installation
:: ---------------------------------------------------------------------------

echo 🔍 Checking for ImageMagick...
magick -version >nul 2>&1
if errorlevel 1 (
    echo 🚀 Installing latest ImageMagick...
    winget install --silent --accept-package-agreements --accept-source-agreements ImageMagick.ImageMagick
    if errorlevel 1 goto :ErrorInstallMagick
) else (
    echo ✅ ImageMagick detected.
)
echo.

:: ---------------------------------------------------------------------------
::  5. PATH Configuration
:: ---------------------------------------------------------------------------

echo 🔧 Adding "%CURRENT_DIR%" to system PATH...
echo %PATH% | find /i "%CURRENT_DIR%" >nul
if errorlevel 1 (
    setx PATH "%PATH%;%CURRENT_DIR%"
    echo ✅ PATH updated.
) else (
    echo ✅ Already in PATH.
)
echo.

:: ---------------------------------------------------------------------------
::  6. Create magic.bat Wrapper
:: ---------------------------------------------------------------------------

:: We always recreate it to ensure it matches the Gold Standard version
echo 📄 Updating magic.bat...
(
    echo @echo off
    echo setlocal EnableExtensions DisableDelayedExpansion
    echo.
    echo :: ===========================================================================
    echo ::  Script: magic.bat
    echo ::  Description: Portable batch wrapper for the Magick Image CLI ^(magic.py^).
    echo ::               Ensures the Python environment is ready and passes all
    echo ::               arguments correctly to the Python script.
    echo ::  Author: Antigravity
    echo ::  License: MIT
    echo :: ===========================================================================
    echo.
    echo :: ---------------------------------------------------------------------------
    echo ::  1. Setup Environment
    echo :: ---------------------------------------------------------------------------
    echo.
    echo :: Get the directory where this batch file resides.
    echo set "SCRIPT_DIR=%%~dp0"
    echo.
    echo :: Define the path to the core Python script.
    echo set "PYTHON_SCRIPT=%%SCRIPT_DIR%%magic.py"
    echo.
    echo :: ---------------------------------------------------------------------------
    echo ::  2. Validation Checks
    echo :: ---------------------------------------------------------------------------
    echo.
    echo :: Check if magic.py actually exists in the same folder.
    echo if not exist "%%PYTHON_SCRIPT%%" goto :ErrorMissingFile
    echo.
    echo :: Check if Python is installed and available in the system PATH.
    echo python --version ^>nul 2^>^&1
    echo if errorlevel 1 goto :ErrorNoPython
    echo.
    echo :: ---------------------------------------------------------------------------
    echo ::  3. Execution
    echo :: ---------------------------------------------------------------------------
    echo.
    echo :: Run the Python script, passing all command-line arguments ^(%%*^) forward.
    echo python "%%PYTHON_SCRIPT%%" %%*
    echo.
    echo :: Capture the exit code from the Python script to propagate it.
    echo set "EXIT_CODE=%%errorlevel%%"
    echo.
    echo :: ---------------------------------------------------------------------------
    echo ::  4. Exit
    echo :: ---------------------------------------------------------------------------
    echo.
    echo :: Exit with the same status code as the Python script.
    echo exit /b %%EXIT_CODE%%
    echo.
    echo :: ---------------------------------------------------------------------------
    echo ::  Error Handlers
    echo :: ---------------------------------------------------------------------------
    echo.
    echo :ErrorMissingFile
    echo echo [ERROR] Critical file missing: "%%PYTHON_SCRIPT%%"
    echo echo Please ensure magic.py is in the same directory as this batch file.
    echo exit /b 1
    echo.
    echo :ErrorNoPython
    echo echo [ERROR] Python is not found in your PATH.
    echo echo Please install Python ^(https://www.python.org/^) or run setup_magic.bat.
    echo exit /b 1
) > "%CURRENT_DIR%\magic.bat"
echo ✅ magic.bat updated.
echo.

:: ---------------------------------------------------------------------------
::  7. Final Verification
:: ---------------------------------------------------------------------------

if not exist "%CURRENT_DIR%\magic.py" (
    echo ⚠️  magic.py not found in this folder!
    echo Please place your magic.py file here.
    pause
    exit /b 1
)

echo =======================================================
echo ✅ Setup complete!
echo You can now use the "magic" command anywhere.
echo Example:
echo   magic 720p q80 Profile.jpg
echo =======================================================
pause
exit /b 0

:: ---------------------------------------------------------------------------
::  Error Handlers
:: ---------------------------------------------------------------------------

:ErrorNoAdmin
echo ⚠️  Please run this script as Administrator!
echo    Right-click -> Run as Administrator
pause
exit /b 1

:ErrorInstallPython
echo ❌ Failed to install Python.
pause
exit /b 1

:ErrorInstallDeps
echo ❌ Failed to install dependencies. Check your internet connection.
pause
exit /b 1

:ErrorInstallMagick
echo ❌ Failed to install ImageMagick.
pause
exit /b 1

