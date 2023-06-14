from time import sleep
import ui
import frametools
import save
import overheat
import config

# Load sensor type from config and load required module
from importlib import import_module
sensor = import_module("sensor." + config.SENSOR)

import trigger
import monitor
import buzzer


monitor_temps = config.TEST_PIXELS

monitor_list = config.TEST_ARRAY
trigger_list = config.PIXEL_TRIGGER_ARRAY
trigger_visual = config.PIXEL_TRIGGER
trigger_periodic = config.PERIODIC_TRIGGER


while True:
    # Get latest frame from Sensor
    frame_raw = sensor.get_frame()

    # Temporarily store frame. Get the frame with "frametools.frame_store[n]. n 0 is the oldest, n -1 the newest frame."
    frametools.store(frame_raw)
    frame_latest = frametools.frame_store[-1]
    utime_latest = frametools.utime_store[-1]

    overheat.cpu_protect()

    if monitor_temps:
        monitor.temps(frame_latest, monitor_list)

    if trigger_visual:
        trigger.visual(frame_latest, trigger_list)

    if trigger_periodic:
        trigger.periodic()

    # Check if save has been triggered
    save.pending()

    # Apply emissivity adjustment
    frame_adjusted = frametools.adjust_emissivity(frame_latest)
    # Display frame
    ui.refresh(frame_adjusted, utime_latest)