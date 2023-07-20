import numpy as np
from modules.pylepton.Lepton3 import Lepton3
from modules.v4l2lepton3.control import Lepton3Control as l_ctrl
from .lepton35_prop import SENSOR_SHAPE
from time import sleep




def i2c_command(command_name, method_name, parameter = None):
    result, error_code = lepton.execute_command(command_name, method_name, parameter)

    return result, error_code

i2c_number = 1
try:
    #print("Connecting to Lepton CCI via I2C...")
    lepton = l_ctrl(i2c_number)

    #print("Setting 'sys_gain_mode' to 'auto'...")
    i2c_command("sys_gain_mode", "SET", parameter="auto")
    gain_mode_result, gain_mode_error_code = i2c_command("sys_gain_mode", "GET")
    #print("sys_gain_mode: " + gain_mode_result + "     error_code: " + str(gain_mode_error_code) + "\n")

except Exception as e:
    import traceback

    traceback.print_exc()
    print(str(e))
    print("CCI is not necessary for Lepton to work, but settings could not be applied. \nContinuing anyways...\n")



spi_path = "/dev/spidev0.0"
def get_frame(device = spi_path):
    while True:
        with Lepton3(device) as lepton:
            frame_array, _ = lepton.capture()
        frame_array = np.float_(frame_array) # Set datatype to float
        frame_array = frame_array.flatten() # Flatten array to remove unnecessary brackets.
        frame_array = np.reshape(frame_array, SENSOR_SHAPE)  # Reshape array to Sensor size. Results in 2D array
        frame_array /= 100 # Convert cK to K

        if not garbage(frame_array): # Workaround for occasional garbage frames
            break
        else:
            sleep(0.1)

    return frame_array

# If a value in the frame is around absolute zero, it's garbage.
# This is the workaround till I figure out how to use the i2c
def garbage(frame):
    temp_min = np.min(frame)
    temp_max = np.max(frame)
    if temp_min < 50 or temp_max > 773.15:
        return True
    else:
        return False