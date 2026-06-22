@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File bootstrap\windows.ps1
pause
