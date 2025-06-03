@echo off
setlocal

set ENV_NAME=replicant_fishing_bot
set PYTHON_VERSION=3.11

:: Check if env exists
conda info --envs | findstr /C:"%ENV_NAME%" >nul
if %ERRORLEVEL% EQU 0 (
    echo Conda environment "%ENV_NAME%" already exists.
) else (
    echo Creating conda environment "%ENV_NAME%" with Python %PYTHON_VERSION%...
    conda create -y -n %ENV_NAME% python=%PYTHON_VERSION%
)

echo Activating environment...
call conda activate %ENV_NAME%

echo Installing/updating packages...
pip install -r requirements.txt

echo.
echo Done! Use 'conda activate %ENV_NAME%' to activate later.
pause
