import configparser
import sys
import traceback
import numpy as np
import os



# Create new config object
def obj():
    obj = configparser.ConfigParser(inline_comment_prefixes=" #")
    return obj

try:
    arg_path = sys.argv[1]
except IndexError:
    arg_path = "None"

def read(config_file = arg_path):
    # Read config file
    try:
        #config_file = sys.argv[1]
        config = obj()
        config.read(config_file)

    # Catch no config file
    except IndexError:
        print("Missing argument: No file specified!")
        print("Useage: python3 program-name.py /example/path/to/file")
        print("                                ^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(2)

    # return config
    return config

# Save config object to file
def write(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fileObj:
        obj.write(fileObj)
        fileObj.flush()
        fileObj.close()


def get(config, section, option, default = ""):
    if config.has_option(section, option):
        return config.get(section, option)
    else:
        return default



#config = read()



### Variables ###

# Load config file
def get_dict(config = read()):
    ##################################################################################################################
    ###NAME                       =                 type(get(config, section,             option,                optional_default))###
    ##################################################################################################################
    # Hardware
    SENSOR                        =                  get(config, "Hardware",          "sensor",              "unknown")
    BUZZER                        =             eval(get(config, "Hardware",          "buzzer",              "False"))
    BUZZER_PIN                    =              int(get(config, "Hardware",          "buzzer_pin",          "13"))
    LED                           =             eval(get(config, "Hardware",          "led",                 "False"))
    LED_PIN                       =              int(get(config, "Hardware",          "led_pin",             "21"))
    # Accuracy
    EMISSIVITY                    =            float(get(config, "Accuracy",          "emissivity",          "0.95"))  # Emissivity
    # Buttons
    TRIGGER_BUTTON_PINS           =  tuple(map(int, (get(config, "Trigger_Buttons",   "pins",                "12, 26").split(","))))
    # View
    UNIT_TEMPERATURE              =                  get(config, "View",              "unit_temperature",    "celsius") # kelvin, celsius
    INTERPOLATION                 =                  get(config, "View",              "interpolation",       "gaussian")  # none, nearest, bilinear, bicubic, spline16, spline36, hanning, hamming, hermite, kaiser, quadric, catrom, gaussian, bessel, mitchell, sinc, lanczos
    COLORMAP                      =                  get(config, "View",              "colormap",            "nipy_spectral")  # "RdBu_r" #https://matplotlib.org/stable/tutorials/colors/colormaps.html (append "_r" ro get reversed colormap) nipy_spectral default=viridis
    LIMITS                        =             eval(get(config, "View",              "limits_enable",       "False"))
    LIMITS_X                      =             eval(get(config, "View",              "limits_x",            "0, 0"))
    LIMITS_Y                      =             eval(get(config, "View",              "limits_y",            "0, 0"))
    # Temperature Range
    TEMP_RANGE                    =             eval(get(config, "Temperature_Range", "enable",              "False"))  # Temperatures below and above specified values will be ignored and not shown in thermal image if enabled.
    TEMP_RANGE_MIN                =            float(get(config, "Temperature_Range", "min",                 "273.15"))  # -40 °C
    TEMP_RANGE_MAX                =            float(get(config, "Temperature_Range", "max",                 "373.15"))  # 300 °C
    TEMP_RANGE_AUTOADJUST         =             eval(get(config, "Temperature_Range", "auto_adjust", "False"))  # If lower or upper temp doesn't need to be clipped, colorbar only goes to the bound of measured temp. (kinda like autgain)
    # Monitor
    MONITOR                       =             eval(get(config, "Monitor",           "enable",              "False"))  # Monitor pixels. If one or more are not in tolerance, turn screen red. Opptinally send PWM signal to a buzzer.
    MONITOR_INVERT                =             eval(get(config, "Monitor",           "invert",              "False"))
    MONITOR_BUZZER                =             eval(get(config, "Monitor",           "buzzer",              "False"))  # PWM buzzer
    MONITOR_TEST_LIST             =    np.array(eval(get(config, "Monitor",           "test_list",           "[]")))  # Array of pixels to be tested
    MONITOR_MAX_DEVIATIONS        =              int(get(config, "Monitor",           "max_deviations",      "0"))
    # Visual Trigger
    TRIGGER_VISUAL                =             eval(get(config, "Trigger_Visual",    "enable",              "False"))  # If ALL pixels in specified range. Save the oldest frame stored. See: frames_keep_amount. Set to 0 for current frame.
    TRIGGER_VISUAL_INVERT         =             eval(get(config, "Trigger_Visual",    "invert",              "False"))
    TRIGGER_VISUAL_TEST_LIST      =    np.array(eval(get(config, "Trigger_Visual",    "test_list",           "[]")))  # Which pixels to test.
    TRIGGER_VISUAL_MAX_DEVIATIONS =              int(get(config, "Trigger_Visual",    "max_deviations",      "0"))
    TRIGGER_VISUAL_PREVIOUS_FRAME =              int(get(config, "Trigger_Visual",    "previous_frame",      "0"))  # Number of past frames to keep.
    # Save Interval
    TRIGGER_PERIODIC              =             eval(get(config, "Trigger_Periodic",  "enable",              "False"))
    TRIGGER_PERIODIC_INTERVAL     =              int(get(config, "Trigger_Periodic",  "interval",            "60"))
    # Save
    SAVE_PREFIX                   =                  get(config, "Save",              "prefix",              "THC_")
    SAVE_SUFFIX                   =                  get(config, "Save",              "suffix")
    SAVE_PATH                     =                  get(config, "Save",              "path",                "/home/pi/thcam/saves/default")
    SAVE_RAW                      =             eval(get(config, "Save",              "raw",                 "True"))
    SAVE_IMAGE                    =             eval(get(config, "Save",              "image",               "True"))
    SAVE_IMAGE_FORMAT             =                  get(config, "Save",              "image_format",        "png")  # ps, eps, pdf, pgf, png, raw, rgba, svg, svgz, jpg, jpeg, tif, tiff
    SAVE_BUZZER                   =             eval(get(config, "Save",              "buzzer",              "False"))
    SAVE_LED                      =             eval(get(config, "Save",              "led",                 "False"))
    # Feed
    FEED                          =             eval(get(config, "Feed",              "enable",              "False"))
    FEED_PATH                     =                  get(config, "Feed",              "path",                "/home/pi/thcam/feed")
    FEED_LENGTH                   =              int(get(config, "Feed",              "length",              "9"))
    # Frame
    TIMESTAMP                     =              int(get(config, "Frame",             "timestamp",           "0"))
    FRAME                         =    np.array(eval(get(config, "Frame",             "frame",               "[]")))

    VERSION                       =            float(get(config, "File",              "version",             "0"))
    if config.has_section("File"):
        #VERSION = float(get(config, "File", "version"))

        if VERSION == 2.0:
            pass
        elif VERSION < 2.0:
            import warnings
            warnings.warn("Old File.", PendingDeprecationWarning)

            EMISSIVITY = float(get(config, "Settings", "emissivity"))
            INTERPOLATION = get(config, "Settings", "interpolation", "gaussian")
            COLORMAP = get(config, "Settings", "colormap", "viridis")
            TEMP_RANGE = eval(get(config, "Frame", "temp_range", "True"))
            TEMP_RANGE_MIN = float(get(config, "Frame", "temp_range_min"))
            TEMP_RANGE_MAX = float(get(config, "Frame", "temp_range_max"))
            TEMP_RANGE_AUTOADJUST = eval(get(config, "Frame", "auto_adjust_tempbar", "True"))
            FRAME = np.array(eval(get(config, "Frame", "frame", "[]"))) + 273.15 # Convert to Kelvin
        else:
            import printf  # Import here due to circular import conflict

            printf.error("File version " + str(VERSION) + " not supported!")
            sys.exit(3)

    # Create a dictionary to access the settings
    conf_dict = {
        "sensor": SENSOR,
        "emissivity": EMISSIVITY,
        "trigger_button_pins": TRIGGER_BUTTON_PINS,
        "buzzer": BUZZER,
        "buzzer_pin": BUZZER_PIN,
        "led": LED,
        "led_pin": LED_PIN,
        "unit_temperature": UNIT_TEMPERATURE,
        "interpolation": INTERPOLATION,
        "colormap": COLORMAP,
        "limits": LIMITS,
        "limits_x": LIMITS_X,
        "limits_y": LIMITS_Y,
        "temp_range": TEMP_RANGE,
        "temp_range_min": TEMP_RANGE_MIN,
        "temp_range_max": TEMP_RANGE_MAX,
        "temp_range_autoadjust": TEMP_RANGE_AUTOADJUST,
        "monitor": MONITOR,
        "monitor_invert": MONITOR_INVERT,
        "monitor_buzzer": MONITOR_BUZZER,
        "monitor_test_list": MONITOR_TEST_LIST,
        "monitor_max_deviations": MONITOR_MAX_DEVIATIONS,
        "trigger_visual": TRIGGER_VISUAL,
        "trigger_visual_invert": TRIGGER_VISUAL_INVERT,
        "trigger_visual_test_list": TRIGGER_VISUAL_TEST_LIST,
        "trigger_visual_max_deviations": TRIGGER_VISUAL_MAX_DEVIATIONS,
        "trigger_visual_previous_frame": TRIGGER_VISUAL_PREVIOUS_FRAME,
        "trigger_periodic": TRIGGER_PERIODIC,
        "trigger_periodic_interval": TRIGGER_PERIODIC_INTERVAL,
        "save_prefix": SAVE_PREFIX,
        "save_suffix": SAVE_SUFFIX,
        "save_path": SAVE_PATH,
        "save_raw": SAVE_RAW,
        "save_image": SAVE_IMAGE,
        "save_image_format": SAVE_IMAGE_FORMAT,
        "save_buzzer": SAVE_BUZZER,
        "save_led": SAVE_LED,
        "feed": FEED,
        "feed_path": FEED_PATH,
        "feed_length": FEED_LENGTH,
        "timestamp": TIMESTAMP,
        "frame": FRAME,
        "version": VERSION
    }

    return conf_dict
