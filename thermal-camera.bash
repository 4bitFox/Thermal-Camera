#!/bin/bash

cd /home/pi/thcam
python3 -u program/main.py configs/default.conf > >(tee -a thcam.log) 2> >(tee -a thcam.err >&2)

exit
