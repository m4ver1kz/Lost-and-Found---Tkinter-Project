@echo off
setlocal enabledelayedexpansion

title Lost and Found - Java Backend Server

echo ======================================================================
echo Starting Lost and Found Management System - Java Backend
echo ======================================================================

:: 1. Detect and configure JAVA_HOME
if not defined JAVA_HOME (
    if exist "C:\Program Files\Java\jdk-25.0.2" (
        set JAVA_HOME=C:\Program Files\Java\jdk-25.0.2
    ) else if exist "C:\Program Files\Java\jdk-21" (
        set JAVA_HOME=C:\Program Files\Java\jdk-21
    ) else if exist "C:\Program Files\Java\jdk-17" (
        set JAVA_HOME=C:\Program Files\Java\jdk-17
    )
)

where java >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if not defined JAVA_HOME (
        echo [ERROR] Java is not detected on your system PATH or JAVA_HOME.
        echo Please install JDK 17 or later and configure JAVA_HOME.
        pause
        exit /b 1
    )
)

:: 2. Check if MySQL is listening on port 3306
netstat -ano | findstr /r ":3306.*LISTENING" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] MySQL database is not detected on port 3306.
    echo Attempting to start local MySQL server...
    if exist "d:\APP\start_database.bat" (
        call "d:\APP\start_database.bat"
        timeout /t 2 /nobreak >nul
    ) else (
        echo [ERROR] MySQL is required before launching the backend.
        echo Please start MySQL on port 3306 and try again.
        pause
        exit /b 1
    )
)

:: 3. Launch Spring Boot application
echo [INFO] Starting Spring Boot on http://localhost:8080...
cd /d "d:\APP\java_backend"

if exist "target\lost-and-found-backend-0.0.1-SNAPSHOT.jar" (
    echo [INFO] Running packaged application JAR...
    java -jar "target\lost-and-found-backend-0.0.1-SNAPSHOT.jar"
) else (
    echo [INFO] Running via Maven wrapper...
    call mvnw.cmd spring-boot:run
)

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Java backend terminated with exit code %ERRORLEVEL%.
    pause
)
