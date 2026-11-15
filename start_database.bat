@echo off
echo Starting local MySQL database server...
if exist "d:\APP\tools\mariadb-10.11.8-winx64\bin\mysqld.exe" (
    start "MySQL Server" /B "d:\APP\tools\mariadb-10.11.8-winx64\bin\mysqld.exe" --datadir="d:\APP\tools\mariadb-data" --port=3306
    echo MySQL is running on port 3306.
) else (
    echo Note: Ensure MySQL Server is started on port 3306.
)
