import RPi.GPIO as GPIO
import save
import config
import monitor
import dt
import printf



def init(cfg = config.get_dict()):
    setup_manual_triggers(cfg)


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

# Set up pins
def setup_manual_triggers(cfg = config.get_dict()):
    pins = cfg["trigger_button_pins"]
    for pin in pins:
        manual_trigger(pin)



# Take a picture based on the temperature of specific pixels
_autosave_triggered = True #Store autosave state to prevent repeated saving.
_printf_visual_trigger_percent = -1
def visual(frame, trigger_list, cfg = config.get_dict()):
    global _autosave_triggered
    global _printf_visual_trigger_percent

    trigger_visual_invert = cfg["trigger_visual_invert"]
    pixel_trigger_max_deviations = cfg["trigger_visual_max_deviations"]

    result = monitor.test_area(frame, trigger_list) # Test if pixels in tolerance
    result_percent = 100 / (result[0] + result[1]) * result[0]
    if not trigger_visual_invert: # Opposite behaviour to monitor.py => temps()
        result_percent = 100 - result_percent

    # Print when percent changes
    if round(_printf_visual_trigger_percent) != round(result_percent):
        printf.visual_trigger_percent(result_percent)
        _printf_visual_trigger_percent = result_percent

    # Trigger a save, if fewer than the maximum of pixels deviate.
    if result_percent >= 100 - pixel_trigger_max_deviations:
        if not _autosave_triggered:
            save.queue()
            _autosave_triggered = True
    else:
        if _autosave_triggered:
            _autosave_triggered = False



# Save pictures periodically
_utime_store = dt.unix()

def periodic(cfg = config.get_dict()):
    global _utime_store

    trigger_periodic_interval = cfg["trigger_periodic_interval"]

    utime_now = dt.unix()
    #print(utime_store - utime_now)
    if _utime_store <= utime_now:
        save.queue()
        _utime_store = utime_now + trigger_periodic_interval
