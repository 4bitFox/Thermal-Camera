import numpy as np
from modules.pylepton.Lepton3 import Lepton3
from .lepton35_prop import SENSOR_SHAPE, EMISSIVITY_BASELINE

path = "/dev/spidev0.0"
lepton = Lepton3(path)


def get_frame():
    a,_ = lepton.capture()

    np.right_shift(a, 8, a)

    frame = np.reshape(a, SENSOR_SHAPE)  # Reshape array to Sensor size. Results in 2D list
    return frame
