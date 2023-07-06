import numpy as np
from modules.pylepton.Lepton3 import Lepton3
from .lepton35_prop import SENSOR_SHAPE
from time import sleep

path = "/dev/spidev0.0"


def get_frame(device = path):
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
    if temp_min < 50 or temp_max > 600:
        return True
    else:
        return False



# Various attempts to get I2C to work. I gave up for now...
"""
# https://groupgets-files.s3.amazonaws.com/lepton/Resources/110-0144-04%20Rev303%20Lepton%20Software%20Interface%20Description%20Document.pdf
i2c_adress    = 0x2a

# Registers 16 bits
i2c_r_power   = 0x0000
i2c_r_status  = 0x0002
i2c_r_command = 0x0004
i2c_r_length  = 0x0006
i2c_r_data00  = 0x0008
i2c_r_data01  = 0x000A
i2c_r_data02  = 0x000C
i2c_r_data03  = 0x000E
i2c_r_data04  = 0x0010
i2c_r_data05  = 0x0012
i2c_r_data06  = 0x0014
i2c_r_data07  = 0x0016
i2c_r_data08  = 0x0018
i2c_r_data09  = 0x001A
i2c_r_data10  = 0x001C
i2c_r_data11  = 0x001E
i2c_r_data12  = 0x0020
i2c_r_data13  = 0x0022
i2c_r_data14  = 0x0024
i2c_r_data15  = 0x0026



def i2c_():
    import board
    import busio
    import sys
    from bitarray import bitarray

    i2c = busio.I2C(board.SCL, board.SDA)
    if not i2c_adress in i2c.scan():
        print("No I2C device found at " + str(hex(i2c_adress)))
        return

    i2c.writeto(i2c_adress, bytes([0x0002]), stop=False)
    #result = bytearray(2)
    result = bitarray(16)
    i2c.readfrom_into(i2c_adress, result)
    print(result)


def i2c__():
    import pigpio
    import bitarray
    pi = pigpio.pi()

    i2c = pi.i2c_open(1, i2c_adress)
    result1 = pi.i2c_read_word_data(i2c, 0x0002)
    result2 = pi.i2c_read_word_data(i2c, 0x0003)
    result = (result1 << 8) | result2
    print(f"Register value: {result:016b}")


def i2c___():
    from smbus import SMBus

    bus = SMBus(1)
    data_high = bus.read_byte_data(0x2a, 0x0002)
    data_low = bus.read_byte_data(0x2a, 0x0003)

    data = (data_high << 8) | data_low
    print(f"{data_high:08b}")
    print(f"{data_low:08b}")
    print(f"Register value: {data:016b}")

def i2c():
    from i2cdevice import Device, Register, BitField

    CONTROL = Register("CONTROL", i2c_r_status, fields=(BitField("busy",  0b0000000000000001, bit_width = 16),
                                                        BitField("ready", 0b0000000000000100, bit_width = 16)))

    lepton = Device(i2c_adress, bit_width=16, registers = (CONTROL, ))

    control = lepton.get("CONTROL")
    busy = control.busy
    ready = control.ready

    print(bin(busy))
    print(bin(ready))

i2c()
"""