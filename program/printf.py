import dt
import config


SAVE_PREFIX = config.SAVE_PREFIX
SAVE_SUFFIX = config.SAVE_SUFFIX


# Abbreiations
ABRV_PERFORMANCE = "PERF"
ABRV_SAVE = "SAVE"
ABRV_BUTTON = "BTTN"
ABRV_PIXEL_TEST = "TEST"
ABRV_AUTOTRIGGER = "ATRG"
ABRV_DEBUG = "DBUG"
AVRV_VALUEERROR = "VERR"
ABRV_OTHERERROR = "OERR"
ABRV_OVERHEATING = "HEAT"

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