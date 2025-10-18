@echo off
title Install Python Bot Framework requirements
echo.
echo This will install the required Python packages for the bot framework.
echo Make sure Python is installed and available in PATH (python --version).
echo.

REM Upgrade pip (recommended)
python -m pip install --upgrade pip

REM Install all required packages
python -m pip install -r requirements.txt

echo.
echo Done! If you saw "Successfully installed", you're good to go.
echo If you get permission errors, try running this window as Administrator.
pause
