import os
import shutil
import traceback
import config
import printf

FILEFORMAT = config.SAVE_FILEFORMAT

#Feed
FEED = config.FEED #When True, save images to feed to be displayed on a html page
LENGTH = config.FEED_LENGTH #How many older pictures to show in the feed
PATH = config.FEED_PATH



# Advance pictures in feed folder by one and delete oldest
def advance(path_newfile):
    # increase file name by 1
    for x in range(LENGTH + 1):
        try:
            fileold = LENGTH - x
            filenew = fileold + 1

            os.rename(PATH + "/" + str(fileold) + "." + FILEFORMAT,
                      PATH + "/" + str(filenew) + "." + FILEFORMAT)
        except FileNotFoundError as e:
            printf.error(str(e))
            traceback.print_exc()
        # delete oldest file
    try:
        os.remove(PATH + "/" + str(LENGTH + 1) + "." + FILEFORMAT)
    except FileNotFoundError as e:
        printf.error(str(e))
        traceback.print_exc()
    # copy file from save directory to feed
    shutil.copy(path_newfile, PATH + "/0." + FILEFORMAT)