import RPi.GPIO as GPIO
from time import sleep
import multiprocessing as mp
import config

GPIO_BUZZER = config.BUZZER_PIN
DUTY_CYCLE = 50 # % duty cycle

#GPIO PWM buzzer
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) # RuntimeWarning: This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.
GPIO.setup(GPIO_BUZZER, GPIO.OUT)

def _buzz(freq, time):
    buzzer = GPIO.PWM(GPIO_BUZZER, freq)
    buzzer.start(DUTY_CYCLE)
    sleep(time)
    buzzer.stop()

# Start a seperate process for buzzing.
def buzz(freq, time):
    buzzer = mp.Process(target=_buzz, args=(freq, time))
    buzzer.start()


# Save chime
def _save_triggered():
    freq1 = 800
    freq2 = 1000
    time_buzz = 0.1
    time_wait = 0.0

    _buzz(freq1, time_buzz)
    sleep(time_wait)
    _buzz(freq2, time_buzz)

def save_triggered():
    buzzer = mp.Process(target=_save_triggered)
    buzzer.start()



def _temp_alarm():
    freq1 = 800
    time_buzz = 0.1

    _buzz(freq1, time_buzz)

# Temps not in tolerance alarm
def temp_alarm():
    buzzer = mp.Process(target=_temp_alarm)
    buzzer.start()


def _overheating_alarm():
    freq1 = 800
    time_buzz = 0.2
    freq2 = 1200

    for i in range(5):
        _buzz(freq1, time_buzz)
        _buzz(freq2, time_buzz)

# Temps not in tolerance alarm
def overheating_alarm():
    buzzer = mp.Process(target=_overheating_alarm)
    buzzer.start()