chcp 65001
cd /d %~dp0
cls


@echo on
python3 csv_to_2D-list.py %1

@echo off
if %errorlevel% neq 0 (
	echo ----------------------------------------------------------------------------------------------------
	color 4
	powershell write-host -back Red -fore White Error %errorlevel%
	pause >nul
	)

exit