@echo off 

echo This script will guide you to install everything you need to run the Viever :-)
pause
cls

echo You will now install Python 3 from the Microsoft Store.
echo I will open the Microsoft Store for you. Install the newest stable version of Python 3 :-)
echo After Python 3 finished installing, close the Microsoft Store and return to this window.
echo If you have Python 3 already installed you can skip this step.
echo Alternatively you can also use the regular Python 3 installer if you so wish. In that case skip this step.
echo To skip this step, close the Microsoft Store after it opens and return to this window.
pause
explorer "ms-windows-store://publisher/?name=Python Software Foundation"

echo ------------------------------------------------------------
echo You can continue here once Python 3 is installed... :-)
pause

cls
echo I will now install the required Python Modules...
echo Installing: matplotlib configparser numpy
sleep 5
pip3 install --upgrade pip
pip3 install --upgrade matplotlib configparser numpy

echo ------------------------------------------------------------
echo All done and dusted! :-)
echo You can now open ".thcam" files with "Thermal-Camera-Viewer.bat".
echo The first time you will have to use "open with" on a ".thcam" file and select "Thermal-Camera-Viewer.bat" to open the file.
echo To make your life easyer, you can check the "Always use this App to open .thcam files." box. ;-)

timeout /T 300
