import RPi.GPIO as GPIO
from time import sleep
import multiprocessing as mp
import config

cfg = config.get_dict()

LED = cfg["led_pin"]


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) # RuntimeWarning: This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.



def setup(pin):
    GPIO.setup(pin, GPIO.OUT)


def state(pin, state):
    if state:
        state_gpio = GPIO.HIGH
    else:
        state_gpio = GPIO.LOW

    GPIO.output(pin, state_gpio)


def _timed(pin, time):
    state(pin, True)
    sleep(time)
    state(pin, False)

def timed(pin, time):
    led_timed = mp.Process(target=_timed, args=(pin, time))
    led_timed.start()


def save():
    timed(LED, 1)


if cfg["led"]:
    setup(LED)