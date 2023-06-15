#!/bin/python3
import os
import time

pause = 3600


def datetime():
    dt = time.strftime("%Y-%m-%d_%H-%M-%S")
    return dt

def temp_cpu():
    temp = os.popen("vcgencmd measure_temp").readline() #Read Raspberry Pi temp
    temp = float(temp.replace("temp=", "").replace("'C", "")) #Remove text and convert to float
    return temp
	
	
while True:
    print(datetime() + "    " + str(temp_cpu()) + "°C")
    time.sleep(pause)
