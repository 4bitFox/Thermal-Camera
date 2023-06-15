#!/bin/sh

cd /home/pi/thcam/misc/pri_log-cpu-temp
python3 -u temp_monitor.py | tee -a temp_cpu.log

exit
