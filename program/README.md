# File Overview

## Runnable scripts

### main.py
Main program that runs the Thermal Camera and loads all the required modules to take pictures, show a preview and much more.

### read.py
Similar to main.py, but it only imports the necessary modules to display a RAW captures that was previously outputted by the main program.

### confgui.py
Creates a graphical user interface to create and edit the camera configuration file. It also allows for editing and viewing RAW captues.

## Modules

### sensor/*.py
Contains the code to get a image from the sensor. The program uses the value from the config to load the correct sensor module.

### sensor/*_prop.py
Contains sensor properties.
- unknown_prop.py tries to get the properties from the RAW temperature data.

### config.py
Responsible to read configuration files and prepare them into a nice dictionary for the rest of the program to use. It also handles saving and creating config objects.

### dt.py
Mainly just returns the datetime in different formats.

### frametools.py
Module with diverse functions to work with the frame data.
- Emissivity adjustment
- Temporary storage of older frames
- Creation of the ROI Overlay for confgui.py
- Creation of a empty frame
- Converting the frame data into a string

### monitor.py
Contains functions that monitor the temperatures the camera sees, check if user specified contitions are met and act accordingy.

### printf.py
Responsible for printing nice and stylish messages to the terminal.

### save.py
Responsible for preparing and saving a RAW file and a Image file.
