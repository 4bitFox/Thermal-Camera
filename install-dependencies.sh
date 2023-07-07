#!/bin/sh

print "Installing required packages..."
sudo apt install python3 python-tk python3-smbus i2c-tools

print "Installing python libraries..."
sudo pip install --upgrade adafruit-circuitpython-mlx90640 adafruit-blinka RPI.GPIO numpy matplotlib configparser PySimpleGUI
