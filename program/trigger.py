import RPi.GPIO as GPIO
import save
import frametools
import config
import monitor
import dt



pins = config.BUTTON_PINS
pixel_trigger_max_deviations = config.PIXEL_TRIGGER_MAX_DEVIATIONS



# Pins that result in a save
def manual_trigger(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=_manual_trigger_callback)

def _manual_trigger_callback(pin): #called when button pressed
    try:
        save.queue()
    except NameError: #If button is pressed to early, frame_array is not defined yet. Catch and ignore :)
        pass

# Set up pins when module is imported

for pin in pins:
    manual_trigger(pin)



# Take a picture based on the temperature of specific pixels
_autosave_triggered = True #Store autosave state to prevent repeated saving.
def visual(frame, trigger_list):
    global _autosave_triggered

    result = monitor.test_pixels(frame, trigger_list) # Test if pixels in tolerance
    if not config.PIXEL_TRIGGER_INVERT:
        # Trigger a save, if fewer than the maximum of pixels deviate.
        if result[1] <= pixel_trigger_max_deviations:
            if not _autosave_triggered:
                save.queue()
                _autosave_triggered = True
        else:
            if _autosave_triggered:
                _autosave_triggered = False
        # Trigger a save if more than the maximum of pixels deviate.
    else:
        if result[1] > pixel_trigger_max_deviations:
            if not _autosave_triggered:
                save.queue()
                _autosave_triggered = True
        else:
            if _autosave_triggered:
                _autosave_triggered = False



# Save pictures periodically
periodic_interval = config.PERIODIC_TRIGGER_INTERVAL
_utime_store = dt.unix()

def periodic():
    global _utime_store

    utime_now = dt.unix()
    #print(utime_store - utime_now)
    if _utime_store <= utime_now:
        save.queue()
        _utime_store = utime_now + periodic_interval
