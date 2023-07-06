#!/bin/python3

import csv
import sys
import re
import traceback
import datetime
import numpy as np
import configparser



PATTERN_RE = re.compile("\d\d[.]\d\d[.]\d\d\s\d\d[:]\d\d[:]\d\d")
PATTERN_DT = "%d.%m.%y %H:%M:%S"



# Read config file
try:
    csv_file = sys.argv[1] # Path to file is argument 1
# Catch no config file
except IndexError as e:
    print(str(e))
    traceback.print_exc()
    print("Missing argument: No input file specified!")
    print("Useage: python3 program-name.py /example/path/to/file.csv")
    print("                                ^^^^^^^^^^^^^^^^^^^^^^^^^")
    sys.exit(2)



# Copied from frametools.py
def stringify(frame):
    # Convert to stringified list
    frame = str(tuple(frame))
    frame = frame.replace("\n", "").replace(". ", "").replace(" ", "").replace("(", "").replace(")", "").replace(
        "array", "").replace(",", ", ")  # Remove unwanted parts
    frame = "[" + frame + "]"  # Add missing brackets
    return frame


# Copied from config.py
def write(obj, path):
    try:
        with open(path, "w") as fileObj:
            obj.write(fileObj)
            fileObj.flush()
            fileObj.close()
    except FileNotFoundError as e:
        print.error(e)
        traceback.print_exc()



temp_list = [] # empty 1D list

with open(csv_file, mode ="r") as file:
    csv_content = csv.reader(file, delimiter=";") # Read csv and separate into columns using ;

    for line in csv_content: # Iterate through all lines
        if len(line) == 3: # Only lines with 3 columns
            if re.match(PATTERN_RE, line[0]): # Only if line matches the pattern
                #print(line[1])
                temp_list.append(float(line[1]))
                datetime_last = line[0]



# Convert string date to unix time
dt = datetime.datetime.strptime(datetime_last, PATTERN_DT)
ut = round(dt.timestamp())


print()
y = int(input("Enter the amount of rows: "))
try:
    array = np.reshape(temp_list, (y, -1))
except ValueError as e:
    print(str(e))
    traceback.print_exc()
    print("Can not split list with length of " + str(len(temp_list)) + " into " + str(y) + " rows!")
    sys.exit(3)

if input("Should I flip the image horizontally? (y/N): ") == "y":
    array = np.fliplr(array)
if input("Should I flip the image vertically? (y/N): ") == "y":
    array = np.flipud(array)

array += 273.15 # Convert to Kelvin

frame = stringify(array)
print()
print("timestamp = " + str(ut))
print("frame = " + frame)
print()




saveinp = input("Do you wish to export to a .thcam file? (y/N): ")

if saveinp == "y":
    rawfile = configparser.ConfigParser(inline_comment_prefixes=" #")

    rawfile.add_section("File")
    rawfile.set("File", "version", "2.0")

    rawfile.add_section("Hardware")
    rawfile.set("Hardware", "sensor", "unknown")

    rawfile.add_section("Accuracy")
    rawfile.set("Accuracy", "emissivity", "1")

    rawfile.add_section("View")
    rawfile.set("View", "interpolation", "none")
    rawfile.set("View", "colormap", "nipy_spectral")

    rawfile.add_section("Save")
    rawfile.set("Save", "prefix", "CSV_")
    rawfile.set("Save", "suffix", "_export")

    rawfile.add_section("Frame")
    rawfile.set("Frame", "timestamp", str(ut))
    rawfile.set("Frame", "frame", frame)

    path = csv_file + ".thcam"
    write(rawfile, path)