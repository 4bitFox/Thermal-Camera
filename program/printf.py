import dt
import config



cfg = config.get_dict()

SAVE_PREFIX = cfg["save_prefix"]
SAVE_SUFFIX = cfg["save_suffix"]


# Abbreiations
ABRV_SAVE = "SAVE"
ABRV_DEBUG = "DBUG"
ABRV_OTHERERROR = "OERR"
ABRV_OVERHEATING = "HEAT"
ABRV_VISUAL_TRIGGER = "VIST"
ABRV_MONITOR = "MONI"

PRINT_DEBUG = True
PRINT_SAVE = True

def printf(type, message):
    message = str(message)
    out = "[ "+ SAVE_PREFIX + dt.simple() + SAVE_SUFFIX + " - " + type + " ]    " + message
    print(out)


def debug(message):
    if PRINT_DEBUG:
        printf(ABRV_DEBUG, message)

def error(message):
    printf(ABRV_OTHERERROR, message)

def save(message):
    if PRINT_SAVE:
        printf(ABRV_SAVE, message)

def overheating(message):
    printf(ABRV_OVERHEATING, message)

def visual_trigger_percent(percent):
    printf(ABRV_VISUAL_TRIGGER, str(round(float(percent), 2)) + " % in range.")

def monitor_percent(percent):
    printf(ABRV_MONITOR, str(round(float(percent), 2)) + " % in range.")