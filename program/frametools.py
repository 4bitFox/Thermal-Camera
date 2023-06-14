import numpy as np
import config
import dt
# Load sensor type from config and load required module
from importlib import import_module
sensor_prop = import_module("sensor." + config.SENSOR + "_prop")

SENSOR_SHAPE = sensor_prop.SENSOR_SHAPE
EMISSIVITY_BASELINE = sensor_prop.EMISSIVITY_BASELINE


emissivity = config.EMISSIVITY


frames_keep_amount = config.FRAMES_KEEP_AMOUNT


# These variables store frames, starting from oldest to newest at the end.
frame_store = [] # Create list to store previous frames.        To get oldest: frame_store[0]    To get newest: frame_store[-1]
utime_store = [] # Create list to store previous timestamps.    To get oldest: utime_store[0]    To get newest: utime_store[-1]


# Create empty 2D array
def empty():
    frame_empty = np.zeros((SENSOR_SHAPE[0], SENSOR_SHAPE[1]), )
    return frame_empty

# Store
def _store_current(frame, unix):
    global frame_store
    global utime_store

    frame_store = [frame]
    utime_store = [unix]


# Store previous frames to be saved later
def _store_previous(frame, unix):
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



def store(frame):
    unix = dt.unix()
    if frames_keep_amount == 0:
        _store_current(frame, unix)
    else:
        _store_previous(frame, unix)

def adjust_emissivity(frame):
    e_comp = EMISSIVITY_BASELINE / emissivity  # Emissivity compensation
    frame = frame.copy()
    frame *= e_comp  # Correct temperature
    return frame

def stringify(frame):
    # Convert to stringified list
    frame = str(tuple(frame))
    frame = frame.replace("\n", "").replace(". ", "").replace(" ", "").replace("(", "").replace(")", "").replace(
        "array", "").replace(",", ", ")  # Remove unwanted parts
    frame = "[" + frame + "]"  # Add missing brackets
    return frame