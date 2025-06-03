@echo off
setlocal

set ENV_DIR=venv

:: Check if venv already exists
if exist %ENV_DIR%\ (
    echo Virtual environment "%ENV_DIR%" already exists.
) else (
    echo Creating virtual environment in "%ENV_DIR%"...
    python -m venv %ENV_DIR%
)

:: Activate the virtual environment
call %ENV_DIR%\Scripts\activate.bat

:: Check if activation succeeded
if errorlevel 1 (
    echo Failed to activate the virtual environment.
    exit /b 1
)

:: Check if requirements.txt exists
if exist requirements.txt (
    echo Installing required packages from requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo No requirements.txt file found. Skipping package installation.
)

echo.
echo Done! Environment is activated.
echo To activate it again later, run:
echo     %ENV_DIR%\Scripts\activate.bat

pause
