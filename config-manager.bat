chcp 65001
cd /d %~dp0
cls

:: Minimize ugly terminal.
@echo off
powershell -window minimized -command ""


:: Run Termal Camera Config Manager
@echo on
python3 program\confgui.py %1

@echo off
if %errorlevel% neq 0 (
	powershell -window normal -command ""
	echo ----------------------------------------------------------------------------------------------------
	color 4
	powershell write-host -back Red -fore White Error %errorlevel%
	pause >nul
	)

exit
