#import warnings
import config


SENSOR_SHAPE = None
SENSOR_EMISSIVITY = 1 #Correct sensor emissivity baseline. (Should not be necessary)

print("Unknown sensor!")


# Try to get resolution from frame:
def sensor_shape(cfg = config.get_dict()):
    if str(cfg["frame"]) != "[]":
        print("Trying to get the sensor resolution from Frame.")
        frame = cfg["frame"]
        y = len(frame)
        x = len(frame[0])
    else:
        raise Exception("Specify a supported sensor in the config file!")
        sys.exit("Unknown Sensor")

    return (y, x)  # resolution of Sensor. Required in all Sensor modules!


def init(cfg = config.get_dict()):
    global SENSOR_SHAPE
    SENSOR_SHAPE = sensor_shape(cfg)
