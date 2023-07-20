chcp 65001
cd /d %~dp0
cd ..\..
cls

:: Minimize ugly terminal.
@echo off
powershell -window minimized -command ""


:: Run Termal Camera
@echo on
%LocalAppData%\thcam\venv\Scripts\python.exe program\read.py %1 --save png

@echo off
if %errorlevel% neq 0 (
	powershell -window normal -command ""
	echo ----------------------------------------------------------------------------------------------------
	color 4
	powershell write-host -back Red -fore White Error %errorlevel%
	pause >nul
	)

exit
