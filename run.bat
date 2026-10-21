@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYW=C:\Users\dell\.workbuddy\binaries\python\envs\deskpet\Scripts\pythonw.exe
if not exist "%PYW%" (
    echo 找不到 Python 环境: %PYW%
    echo 请改用 白蕾丝小姐.exe
    pause
    exit /b 1
)
start "" "%PYW%" main.py
