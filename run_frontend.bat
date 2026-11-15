@echo off
setlocal

title Lost and Found - Desktop GUI

echo ======================================================================
echo Starting Lost and Found Management System - Desktop GUI
echo ======================================================================

:: 1. Check and activate Python virtual environment if present
if exist "d:\APP\venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment in d:\APP\venv...
    call "d:\APP\venv\Scripts\activate.bat"
) else if exist "d:\APP\.venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment in d:\APP\.venv...
    call "d:\APP\.venv\Scripts\activate.bat"
) else if exist "d:\APP\python_frontend\venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment in python_frontend\venv...
    call "d:\APP\python_frontend\venv\Scripts\activate.bat"
)

:: 2. Check Python availability
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found on your system PATH.
    echo Please install Python 3.10 or later and ensure 'python' is accessible.
    pause
    exit /b 1
)

:: 3. Check for requests dependency
python -c "import requests" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Missing 'requests' dependency. Installing now...
    pip install -r "d:\APP\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install required Python packages.
        pause
        exit /b 1
    )
)

:: 4. Launch Desktop GUI Application
echo [INFO] Launching Tkinter Desktop Application...
cd /d "d:\APP\python_frontend"
python main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
