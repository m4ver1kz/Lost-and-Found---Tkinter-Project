@echo off
setlocal enabledelayedexpansion

title Lost and Found Management System - Master Launcher

echo ======================================================================
echo          LOST AND FOUND MANAGEMENT SYSTEM - MASTER LAUNCHER
echo ======================================================================
echo.

:: -------------------------------------------------------------------------
:: STEP 1: Verify MySQL Database Availability (Port 3306)
:: -------------------------------------------------------------------------
echo [STEP 1/3] Checking MySQL database connectivity on port 3306...
netstat -ano | findstr /r ":3306.*LISTENING" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo [WARNING] MySQL is not detected on port 3306.
    echo Attempting to start local MySQL database...
    if exist "d:\APP\start_database.bat" (
        call "d:\APP\start_database.bat"
        echo Waiting for MySQL to initialize...
        
        :: Wait up to 10 seconds for MySQL port 3306
        set MYSQL_READY=0
        for /L %%i in (1,1,10) do (
            timeout /t 1 /nobreak >nul
            netstat -ano | findstr /r ":3306.*LISTENING" >nul 2>&1
            if !ERRORLEVEL! equ 0 (
                set MYSQL_READY=1
                goto :mysql_started
            )
        )
        :mysql_started
        if !MYSQL_READY! neq 1 (
            echo.
            echo [ERROR] MySQL database could not be reached on port 3306.
            echo Please ensure your MySQL service is active and try again.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo [ERROR] MySQL is not running on port 3306.
        echo Please start your MySQL service and ensure database 'lost_and_found' is created.
        pause
        exit /b 1
    )
)
echo [SUCCESS] MySQL database is active on port 3306.
echo.

:: -------------------------------------------------------------------------
:: STEP 2: Check or Launch Java Backend (Spring Boot REST API)
:: -------------------------------------------------------------------------
echo [STEP 2/3] Checking Java backend service...

:: Check if backend is already running and healthy
curl.exe -s http://localhost:8080/api/health | findstr /i "CONNECTED" >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Java backend is already running on port 8080 and connected to MySQL.
) else (
    echo [INFO] Starting Java backend server in a separate process...
    start "Lost and Found Backend" cmd /c "d:\APP\run_backend.bat"

    echo Waiting for backend health confirmation at http://localhost:8080/api/health...
    
    set BACKEND_READY=0
    for /L %%s in (1,1,45) do (
        timeout /t 1 /nobreak >nul
        <nul set /p=.
        curl.exe -s http://localhost:8080/api/health | findstr /i "CONNECTED" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            set BACKEND_READY=1
            echo.
            goto :backend_ready
        )
    )

    :backend_ready
    if !BACKEND_READY! neq 1 (
        echo.
        echo [ERROR] Java backend failed to become healthy within 45 seconds.
        echo Please check the Java backend console window for details.
        pause
        exit /b 1
    )
    echo [SUCCESS] Java backend is verified running and connected to MySQL!
)
echo.

:: -------------------------------------------------------------------------
:: STEP 3: Launch Python Tkinter Desktop GUI
:: -------------------------------------------------------------------------
echo [STEP 3/3] Launching Python Desktop Application...
call "d:\APP\run_frontend.bat"
