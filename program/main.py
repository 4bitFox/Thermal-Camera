#!/usr/bin/env python3


from time import sleep
import ui
ui.init()
import frametools
import save
import overheat
import config

cfg = config.get_dict()

# Load sensor type from config and load required module
from importlib import import_module
sensor = import_module("sensor." + cfg["sensor"])

import trigger
trigger.init()
import monitor


monitor_temps = cfg["monitor"]

monitor_list = cfg["monitor_test_list"]
trigger_list = cfg["trigger_visual_test_list"]
trigger_visual = cfg["trigger_visual"]
trigger_periodic = cfg["trigger_periodic"]


while True:
    # Get latest frame from Sensor
    frame_raw = sensor.get_frame()

    # Temporarily store frame. Get the frame with "frametools.frame_store[n]. n 0 is the oldest, n -1 the newest frame."
    frametools.store(frame_raw)
    frame_latest = frametools.frame_store[-1]
    utime_latest = frametools.utime_store[-1]

    overheat.cpu_protect()

    # Apply adjustments
    frame_adjusted = frametools.adjust_emissivity(frame_latest)  # Emissivity

    if monitor_temps:
        monitor.temps(frame_adjusted, monitor_list)

    if trigger_visual:
        trigger.visual(frame_adjusted, trigger_list)

    if trigger_periodic:
        trigger.periodic()

    # Check if save has been triggered
    save.pending()

    # Display frame
    ui.refresh(frame_adjusted, utime_latest)