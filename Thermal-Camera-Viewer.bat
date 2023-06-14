chcp 65001
cd /d %~dp0
cls

:: Minimize ugly terminal.
@echo off
powershell -window minimized -command ""

:: Run Thermal Camera Viewer
@echo on
python3 program\read.py %1

:: Show terminal again when a Error occurs.
@echo off
if %errorlevel% neq 0 (
	powershell -window normal -command ""
	echo ----------------------------------------------------------------------------------------------------
	color 4
	powershell write-host -back Red -fore White Error %errorlevel%
	pause >nul
	)

exit
