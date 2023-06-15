import configparser
import sys
import traceback
import numpy as np



# Create new config object
def obj():
    obj = configparser.ConfigParser(inline_comment_prefixes=" #")
    return obj

def read():
    # Read config file
    try:
        config_file = sys.argv[1]
        config = obj()
        config.read(config_file)

    # Catch no config file
    except IndexError:
        print("Missing argument: No configuration file specified!")
        print("Useage: python3 program-name.py /example/path/to/configfile")
        print("                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        sys.exit(2)

    # return config
    return config

# Save config object to file
def write(obj, path):
    try:
        with open(path, "w") as fileObj:
            obj.write(fileObj)
            fileObj.flush()
            fileObj.close()
    except FileNotFoundError as e:
        import printf # Import here due to circular import conflict
        printf.error(e)
        traceback.print_exc()


def get(config, section, option, default = ""):
    if config.has_option(section, option):
        return config.get(section, option)
    else:
        return default



config = read()



### Variables ###

# Load config file
try:
    ##################################################################################################################
    ###NAME                      =                 type(get(config, section,             option,                optional_default))###
    ##################################################################################################################
    # Hardware
    SENSOR                       =                  get(config, "Hardware",          "sensor",              "unknown")
    # Accuracy
    EMISSIVITY                   =            float(get(config, "Accuracy",          "emissivity",          "0.95"))  # Emissivity
    # Buttons
    BUTTON_PINS                  =  tuple(map(int, (get(config, "Trigger_Buttons",   "pins",                "12").split(", "))))
    # Buzzer
    BUZZER                       =             eval(get(config, "Buzzer",            "enable",              "False"))
    BUZZER_PIN                   =              int(get(config, "Buzzer",            "pin",                 "13"))
    # View
    INTERPOLATION                =                  get(config, "View",              "interpolation",       "gaussian")  # none, nearest, bilinear, bicubic, spline16, spline36, hanning, hamming, hermite, kaiser, quadric, catrom, gaussian, bessel, mitchell, sinc, lanczos
    COLORMAP                     =                  get(config, "View",              "colormap",            "nipy_spectral")  # "RdBu_r" #https://matplotlib.org/stable/tutorials/colors/colormaps.html (append "_r" ro get reversed colormap) nipy_spectral default=viridis
    LIMITS                       =             eval(get(config, "View",              "limits_enable",       "False"))
    LIMITS_X                     =             eval(get(config, "View",              "limits_x",            "0, 0"))
    LIMITS_Y                     =             eval(get(config, "View",              "limits_y",            "0, 0"))
    # Temperature Range
    TEMP_RANGE                   =             eval(get(config, "Temperature_Range", "enable",              "False"))  # Temperatures below and above specified values will be ignored and not shown in thermal image if enabled.
    TEMP_RANGE_MIN               =              int(get(config, "Temperature_Range", "min",                 "-40"))  # -40 °C
    TEMP_RANGE_MAX               =              int(get(config, "Temperature_Range", "max",                 "300"))  # 300 °C
    AUTO_ADJUST_TEMPBAR          =             eval(get(config, "Temperature_Range", "auto_adjust_tempbar", "False"))  # If lower or upper temp doesn't need to be clipped, colorbar only goes to the bound of measured temp. (kinda like autgain)
    # Monitor
    TEST_PIXELS                  =             eval(get(config, "Monitor",           "enable",              "False"))  # Monitor pixels. If one or more are not in tolerance, turn screen red. Opptinally send PWM signal to a buzzer.
    TEST_INVERT                  =             eval(get(config, "Monitor",           "invert",              "False"))
    TEST_BUZZER                  =             eval(get(config, "Monitor",           "buzzer_enable",       "False"))  # PWM buzzer
    TEST_ARRAY                   =             eval(get(config, "Monitor",           "pixels_list",         "[]"))  # Array of pixels to be tested
    TEST_MAX_DEVIATIONS          =              int(get(config, "Monitor",           "max_deviations",      "0"))
    # Visual Trigger
    PIXEL_TRIGGER                =             eval(get(config, "Trigger_Visual",    "enable",              "False"))  # If ALL pixels in specified range. Save the oldest frame stored. See: frames_keep_amount. Set to 0 for current frame.
    PIXEL_TRIGGER_INVERT         =             eval(get(config, "Trigger_Visual",    "invert",              "False"))
    PIXEL_TRIGGER_ARRAY          =             eval(get(config, "Trigger_Visual",    "pixels_list",         "[]"))  # Which pixels to test.
    PIXEL_TRIGGER_MAX_DEVIATIONS =              int(get(config, "Trigger_Visual",    "max_deviations",      "0"))
    FRAMES_KEEP_AMOUNT           =              int(get(config, "Trigger_Visual",    "previous_frame",      "0"))  # Number of past frames to keep.
    # Save Interval
    PERIODIC_TRIGGER             =             eval(get(config, "Trigger_Periodic",  "enable",              "False"))
    PERIODIC_TRIGGER_INTERVAL    =              int(get(config, "Trigger_Periodic",  "interval",            "60"))
    # Save
    SAVE_PREFIX                  =                  get(config, "Save",              "prefix",              "THC_")
    SAVE_SUFFIX                  =                  get(config, "Save",              "suffix")
    SAVE_PATH                    =                  get(config, "Save",              "path",                "/home/pi/Pictures/thcam")
    SAVE_FILEFORMAT              =                  get(config, "Save",              "format",              "png")  # ps, eps, pdf, pgf, png, raw, rgba, svg, svgz, jpg, jpeg, tif, tiff
    SAVE_BUZZER                  =             eval(get(config, "Save",              "buzzer",              "False"))
    # Feed
    FEED                         =             eval(get(config, "Feed",              "enable",              "False"))
    FEED_PATH                    =                  get(config, "Feed",              "path",                "/home/pi/Pictures/thcam/.feed")
    FEED_LENGTH                  =              int(get(config, "Feed",              "length",              "9"))
    # Frame
    TIMESTAMP                    =              int(get(config, "Frame",             "timestamp",           "0"))
    FRAME                        =    np.array(eval(get(config, "Frame",             "frame",               "[]")))

    if config.has_section("File"):
        VERSION = float(get(config, "File", "version"))

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
            AUTO_ADJUST_TEMPBAR = eval(get(config, "Frame", "auto_adjust_tempbar", "True"))
        else:
            import printf  # Import here due to circular import conflict

            printf.error("File version " + str(VERSION) + " not supported!")
            sys.exit(3)

except Exception as e:
    import printf  # Import here due to circular import conflict

    printf.error(e)
    traceback.print_exc()
