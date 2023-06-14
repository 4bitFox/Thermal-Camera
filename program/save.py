import numpy as np
import config
import frametools
import dt
import ui
import printf
import feed
from importlib import import_module
SENSOR = config.SENSOR
sensor_prop = import_module("sensor." + SENSOR + "_prop")

SENSOR_SHAPE = sensor_prop.SENSOR_SHAPE


#Save
SAVE_IMG = True
SAVE_RAW = True
PREFIX = config.SAVE_PREFIX
SUFFIX = config.SAVE_SUFFIX
PATH = config.SAVE_PATH
FILEFORMAT = config.SAVE_FILEFORMAT
TEMP_ALARM_VISIBLE = True
RAW_ROUND = True #Round array numbers
RAW_ROUND_DECIMALS = 2 #Number of decimal places
BUZZER = config.BUZZER
SAVE_BUZZER = config.SAVE_BUZZER

FEED = config.FEED


# For RAW save #
# Accuracy
emissivity = config.EMISSIVITY
EMISSIVITY_BASELINE = sensor_prop.EMISSIVITY_BASELINE
# View
interpolation = config.INTERPOLATION
colormap = config.COLORMAP
limits = config.LIMITS
limits_x = config.LIMITS_X
limits_y = config.LIMITS_Y
# Temperature Range
temp_range = config.TEMP_RANGE
temp_range_min = config.TEMP_RANGE_MIN
temp_range_max = config.TEMP_RANGE_MAX
auto_adjust_tempbar = config.AUTO_ADJUST_TEMPBAR





save_pending = False #If this is true, a save will be triggered on the next possible occasion


def raw(frame, timestamp):
    if RAW_ROUND:
        frame = np.round(frame, decimals=RAW_ROUND_DECIMALS)

    # Convert frame into single line string to be able to be saved
    frame = frametools.stringify(frame)

    rawfile = config.obj()

    rawfile.add_section("File")
    rawfile.set("File", "version", "2.0")  # Version of file format. Tells the viever to read the file differently, depending on what version it is.

    rawfile.add_section("Hardware")
    rawfile.set("Hardware", "sensor", SENSOR)

    rawfile.add_section("Accuracy")
    rawfile.set("Accuracy", "emissivity", str(emissivity))
    rawfile.set("Accuracy", "emissivity_baseline", str(EMISSIVITY_BASELINE))

    rawfile.add_section("View")
    rawfile.set("View", "interpolation", interpolation)
    rawfile.set("View", "colormap", colormap)
    rawfile.set("View", "limits_enable", str(limits))
    rawfile.set("View", "limits_x", str(limits_x))
    rawfile.set("View", "limits_y", str(limits_y))

    rawfile.add_section("Temperature_Range")
    rawfile.set("Temperature_Range", "enable", str(temp_range))
    rawfile.set("Temperature_Range", "min", str(temp_range_min))
    rawfile.set("Temperature_Range", "max", str(temp_range_max))
    rawfile.set("Temperature_Range", "auto_adjust_tempbar", str(auto_adjust_tempbar))

    rawfile.add_section("Frame")
    rawfile.set("Frame", "timestamp", str(timestamp))
    rawfile.set("Frame", "frame", frame)


    path = PATH + "/" + PREFIX + dt.simple(timestamp) + SUFFIX + ".thcam"
    config.write(rawfile, path)



def image(frame, timestamp):
    global save_pending

    # Apply emissivity
    frame = frametools.adjust_emissivity(frame)

    # Invert UI foreground and background colors to indicate save
    ui.theme(ui.COLOR_BG, ui.COLOR_FG)
    ui.refresh(frame, timestamp)
    # Revert to normal colors
    ui.theme(ui.COLOR_FG, ui.COLOR_BG)
    ui.refresh(frame, timestamp)
    # Save
    path = PATH + "/" + PREFIX + dt.simple(timestamp) + SUFFIX + "." + FILEFORMAT
    ui.plt.savefig(path, format=FILEFORMAT)

    printf.save("Saved " + path)

    save_pending = False # Image has been saved. Not pending anymore

    if FEED:
        feed.advance(path)


# Call this if you want to save on next occasion
# This can be called at any moment.
def queue():
    global save_pending
    save_pending = True
    pass


# When this is called, executes a save if one is pending.
# Should only be called from within the loop, so it executes at the correct time.
def pending():
    if save_pending:
        if BUZZER and SAVE_BUZZER:
            import buzzer
            buzzer.save_triggered() # Acoustic notification for save.
        frame = frametools.frame_store[0]  # Get the wanted frame, be it current or a previous frame.
        timestamp = frametools.utime_store[0] # Get the timestamp of the corresponding frame
        if SAVE_IMG:
            image(frame, timestamp)
        if SAVE_RAW:
            raw(frame, timestamp)