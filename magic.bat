@echo off
REM ==================================================
REM MAGIC.BAT - portable batch wrapper for magic.py
REM ==================================================

REM Get the directory where this batch file resides
set "SCRIPT_DIR=%~dp0"

REM Call Python with magic.py in the same folder, passing all arguments
python "%SCRIPT_DIR%magic.py" %*
