import numpy as np
import config
import dt

# These variables store frames, starting from oldest to newest at the end.
frame_store = [] # Create list to store previous frames.        To get oldest: frame_store[0]    To get newest: frame_store[-1]
utime_store = [] # Create list to store previous timestamps.    To get oldest: utime_store[0]    To get newest: utime_store[-1]


# Create empty 2D array
def empty(cfg = config.get_dict()):
    # Load sensor type from config and load required module
    from importlib import import_module

    sensor_prop = import_module("sensor." + cfg["sensor"] + "_prop")
    if cfg["sensor"] == "unknown":
        sensor_prop.init(cfg) # Unknown sensor needs init function to calculate sensor shape from Frame
    SENSOR_SHAPE = sensor_prop.SENSOR_SHAPE

    frame_empty = np.zeros((SENSOR_SHAPE[0], SENSOR_SHAPE[1]), )
    return frame_empty

# Make a full image where ROI "test-list" entry values are shown as average values and the rest if the image that is undefined is set to -1
# This can then be overlayed with a thermal image to show the areas that are being monitored to be in tolerance.
def overlay_roi(cfg = config.get_dict(), test_list = []):
    # Load sensor type from config and load required module
    from importlib import import_module

    sensor_prop = import_module("sensor." + cfg["sensor"] + "_prop")
    if cfg["sensor"] == "unknown":
        sensor_prop.init(cfg) # Unknown sensor needs init function to calculate sensor shape from Frame
    shape = sensor_prop.SENSOR_SHAPE

    shape_y = shape[0]
    shape_x = shape[1]

    list_overlay = []
    for overlay_y in range(shape_y):
        list_overlay_row = []
        for overlay_x in range(shape_x):
            list_overlay_row_result = []
            list_rows = np.shape(test_list)[0]
            for row in range(list_rows):
                list_y = range(int(test_list[row][0]), int(test_list[row][2] + 1))
                list_x = range(int(test_list[row][1]), int(test_list[row][3] + 1))

                if overlay_y in list_y and overlay_x in list_x:
                    average = np.average([test_list[row][4], test_list[row][5]])
                    list_overlay_row_result.append(average)
                else:
                    list_overlay_row_result.append(-1)
            list_overlay_row.append(np.max(list_overlay_row_result))
        list_overlay.append(list_overlay_row)

    return list_overlay



# Store
def _store_current(frame, unix):
    global frame_store
    global utime_store

    frame_store = [frame]
    utime_store = [unix]


# Store previous frames to be saved later
def _store_previous(frame, unix, frames_keep_amount):
    global frame_store
    global utime_store

    # Store previous frames to list.
    # The front of the list always contains the oldest frame. New frames are appended.
    # When frames_keep_amount +1 is exceeded, the oldest frame is purged.
    frame_store.append(frame.copy())  # Append current frame to the end of list. ".copy()" required!
    utime_store.append(unix) # Append timestamp to the end of list.
    if len(frame_store) > frames_keep_amount + 1:
        frame_store.pop(0)  # Delete the oldest frame
        utime_store.pop(0) # Delete oldest timestamp



def store(frame, cfg = config.get_dict()):
    unix = dt.unix()

    frames_keep_amount = cfg["trigger_visual_previous_frame"]

    if frames_keep_amount == 0:
        _store_current(frame, unix)
    else:
        _store_previous(frame, unix, frames_keep_amount)


# Emissivity calculation according to Stefan Bolzmann law.
# Given: T_1, ϵ_1, ϵ_2    Wanted: T_2
# P= ϵ_1 * σ * A * T_1^4 = ϵ_2 * σ * A * T_2^4
# ϵ_1 * T_1^4 = ϵ_2 * T_2^4
# T_2^4 = ϵ_1/ϵ_2 * T_1^4
# T_2 = ∜(ϵ_1/ϵ_2 * T_1^4)
def adjust_emissivity(frame, cfg = config.get_dict()):
    # Load sensor type from config and load required module
    from importlib import import_module

    sensor_prop = import_module("sensor." + cfg["sensor"] + "_prop")
    SENSOR_EMISSIVITY = sensor_prop.SENSOR_EMISSIVITY

    emissivity = cfg["emissivity"]

    emissivity_correction = SENSOR_EMISSIVITY / emissivity # ϵ_1/ϵ_2
    if emissivity_correction != 1:
        frame = frame.copy()
        frame **= 4 # T_1^4
        frame *= emissivity_correction # "(T_1^4)" * "(ϵ_1/ϵ_2)"
        frame **= 1/4 # ∜"(ϵ_1/ϵ_2 * T_1^4)"
    return frame # T_2



def stringify(array):
    # Convert to stringified list
    array = str(tuple(array))
    array = array.replace("\n", "").replace(". ", "").replace(" ", "").replace("(", "").replace(")", "").replace(
        "array", "").replace(",", ", ")  # Remove unwanted parts
    array = "[" + array + "]"  # Add missing brackets
    return array