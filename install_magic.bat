@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Magic Web Installer

echo.
echo =======================================================
echo             🪄 MAGIC WEB INSTALLER
echo =======================================================
echo.

:: ---------------------------------------------------------------------------
::  1. Admin Check
:: ---------------------------------------------------------------------------
net session >nul 2>&1
if errorlevel 1 goto :ErrorNoAdmin

:: ---------------------------------------------------------------------------
::  2. Tool Checks
:: ---------------------------------------------------------------------------
where curl >nul 2>&1
if errorlevel 1 goto :ErrorNoCurl

:: ---------------------------------------------------------------------------
::  3. Install ImageMagick
:: ---------------------------------------------------------------------------
echo [1/4] Checking for ImageMagick...
magick -version >nul 2>&1
if not errorlevel 1 goto :MagickInstalled

echo [INFO] ImageMagick not found. Installing via Winget...
winget install --silent --accept-package-agreements --accept-source-agreements ImageMagick.ImageMagick
if errorlevel 1 goto :ErrorInstallMagick

:MagickInstalled
echo [OK] ImageMagick is ready.
echo.

:: ---------------------------------------------------------------------------
::  4. Setup Install Directory
:: ---------------------------------------------------------------------------
set "INSTALL_DIR=%LOCALAPPDATA%\Magick"
set "TARGET_EXE=%INSTALL_DIR%\magic.exe"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: ---------------------------------------------------------------------------
::  5. Check for Updates
:: ---------------------------------------------------------------------------
echo [2/4] Updating Magic...
set "DOWNLOAD_URL=https://github.com/absaralam/magic-image-cli/releases/latest/download/magic.exe"
goto :Download

:: (Update check removed for stability)
echo.

:: ---------------------------------------------------------------------------
::  6. Download Magic.exe
:: ---------------------------------------------------------------------------
:Download
echo [3/4] Downloading Magic.exe...

curl -L -o "%TARGET_EXE%" "%DOWNLOAD_URL%"
if errorlevel 1 goto :ErrorDownload

if not exist "%TARGET_EXE%" goto :ErrorDownloadMissing

echo [OK] Download complete.
echo.

:: ---------------------------------------------------------------------------
::  7. Add to PATH
:: ---------------------------------------------------------------------------
:ConfigurePath
echo [4/4] Configuring System PATH...
echo %PATH% | find /i "%INSTALL_DIR%" >nul
if errorlevel 1 (
    setx PATH "%PATH%;%INSTALL_DIR%"
    echo [OK] Added to PATH.
    echo [NOTE] You may need to restart your terminal/PC for this to take effect.
) else (
    echo [OK] Already in PATH.
)
echo.

echo =======================================================
echo 🎉 INSTALLATION COMPLETE!
echo You can now use 'magic' from anywhere.
echo Try typing: magic --help
echo =======================================================
pause
exit /b 0

:: ---------------------------------------------------------------------------
::  Error Handlers
:: ---------------------------------------------------------------------------

:ErrorNoAdmin
echo.
echo [ERROR] Please run this script as Administrator!
pause
exit /b 1

:ErrorNoCurl
echo.
echo [ERROR] 'curl' is missing.
pause
exit /b 1

:ErrorInstallMagick
echo.
echo [ERROR] Failed to install ImageMagick.
pause
exit /b 1

:ErrorDownload
echo.
echo [ERROR] Failed to download magic.exe.
pause
exit /b 1

:ErrorDownloadMissing
echo.
echo [ERROR] Download appeared to succeed but file is missing.
pause
exit /b 1
