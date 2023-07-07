import time

FORMAT_SIMPLE = "%Y-%m-%d_%H-%M-%S"
FORMAT_ISO    = "%Y-%m-%d %H:%M:%S"

# Format unix time to human readable format. If no unix time given, return current time
def simple(unix = None):
    if unix == None: # Default parameter is only computed once. This is the workaround...
        unix = time.time()

    localtime = time.localtime(unix)
    str = time.strftime(FORMAT_SIMPLE, localtime)
    return str

# Format unix time to human readable format. If no unix time given, return current time
def iso(unix = None):
    if unix == None: # Default parameter is only computed once. This is the workaround...
        unix = time.time()

    localtime = time.localtime(unix)
    str = time.strftime(FORMAT_ISO, localtime)
    return str

def unix():
    # Get unix time and round to seconds
    unix = round(time.time())
    return unix