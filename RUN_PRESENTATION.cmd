@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\start-regulatrace.ps1"
if errorlevel 1 pause
