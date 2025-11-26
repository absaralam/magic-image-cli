@echo off
setlocal EnableExtensions DisableDelayedExpansion

:: ===========================================================================
::  Script: magic.bat
::  Description: Portable batch wrapper for the Magick Image CLI (magic.py).
::               Ensures the Python environment is ready and passes all
::               arguments correctly to the Python script.
::  Author: Antigravity
::  License: MIT
:: ===========================================================================

:: ---------------------------------------------------------------------------
::  1. Setup Environment
:: ---------------------------------------------------------------------------

:: Get the directory where this batch file resides.
:: %~dp0 expands to the Drive and Path of argument 0 (the script itself).
set "SCRIPT_DIR=%~dp0"

:: Define the path to the core Python script.
set "PYTHON_SCRIPT=%SCRIPT_DIR%magic.py"

:: ---------------------------------------------------------------------------
::  2. Validation Checks
:: ---------------------------------------------------------------------------

:: Check if magic.py actually exists in the same folder.
if not exist "%PYTHON_SCRIPT%" goto :ErrorMissingFile

:: Check if Python is installed and available in the system PATH.
:: We try to run python --version and suppress output.
python --version >nul 2>&1
if errorlevel 1 goto :ErrorNoPython

:: ---------------------------------------------------------------------------
::  3. Execution
:: ---------------------------------------------------------------------------

:: Run the Python script, passing all command-line arguments (%*) forward.
:: We use "%*" to ensure arguments with spaces are handled correctly.
python "%PYTHON_SCRIPT%" %*

:: Capture the exit code from the Python script to propagate it.
set "EXIT_CODE=%errorlevel%"

:: ---------------------------------------------------------------------------
::  4. Exit
:: ---------------------------------------------------------------------------

:: Exit with the same status code as the Python script.
exit /b %EXIT_CODE%

:: ---------------------------------------------------------------------------
::  Error Handlers
:: ---------------------------------------------------------------------------

:ErrorMissingFile
echo [ERROR] Critical file missing: "%PYTHON_SCRIPT%"
echo Please ensure magic.py is in the same directory as this batch file.
exit /b 1

:ErrorNoPython
echo [ERROR] Python is not found in your PATH.
echo Please install Python (https://www.python.org/) or run setup_magic.bat.
exit /b 1
