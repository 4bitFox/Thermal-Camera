import warnings
import config


warnings.warn("Unknown sensor! Specify compatible sensor in config file.", UserWarning)

conf = config.read()

# Try to get resolution from frame:
if conf.has_option("Frame", "frame"):
    print("Trying to get the resolution from Frame instead.")
    frame = config.FRAME
    y = len(frame)
    x = len(frame[0])

    SENSOR_SHAPE = (y, x)  # resolution of Sensor. Required in all Sensor modules!

else:
    raise Exception("Specify a supported sensor in the config file!")
    sys.exit("Unknown Sensor")



EMISSIVITY_BASELINE = 1 #Correct sensor emissivity baseline. (Should not be necessary)