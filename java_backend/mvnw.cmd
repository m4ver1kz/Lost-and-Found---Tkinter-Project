@echo off
if not defined JAVA_HOME set JAVA_HOME=C:\Program Files\Java\jdk-25.0.2
if exist "d:\APP\tools\apache-maven-3.9.9\bin\mvn.cmd" (
    call "d:\APP\tools\apache-maven-3.9.9\bin\mvn.cmd" %*
) else (
    call mvn %*
)
