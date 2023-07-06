import board, busio
from time import sleep
import numpy as np
import adafruit_mlx90640
import traceback
import printf
from .mlx90640_prop import SENSOR_SHAPE

i2c = busio.I2C(board.SCL, board.SDA, frequency=500000) #GPIO I2C frequency

mlx = adafruit_mlx90640.MLX90640(i2c) #Start MLX90640
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ #Refresh rate 1, 2, 4, 8, 16, 32, 64 HZ possible

# Create 1D array to store empty frame
frame_array_new = np.zeros(SENSOR_SHAPE[0] * SENSOR_SHAPE[1])

def get_frame():
    #rarely mlx.getFrame() fails because of I/O error. In that case sleep 1 second and retry.
    while True:
        try:
            mlx.getFrame(frame_array_new) #read MLX temperatures into variable
            break
        except OSError as e:
            printf("error_other", str(e) + " (while getting next frame)")
            traceback.print_exc()
            sleep(1)
    frame_array = frame_array_new #Store read frame into variable
    frame_array = np.reshape(frame_array, SENSOR_SHAPE) #Reshape array to Sensor size. Results in 2D array
    frame_array = np.fliplr(frame_array) #Flip array left to right
    frame_array += 273.15
    return frame_array
