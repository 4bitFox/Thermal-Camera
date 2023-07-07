from time import sleep
import os
import printf
import ui
import config

OVERHEAT_ALERT_TEMP = 80 #Temperature to start alert
OVERHEAT_ALERT_BUZZER = True #Alert with buzzer
OVERHEAT_POWEROFF = True #Poweroff when too hot
OVERHEAT_POWEROFF_TEMP = 87 #Poweroff temp

cfg = config.get_dict()

def temp_cpu():
    temp = os.popen("vcgencmd measure_temp").readline() #Read Raspberry Pi temp
    temp = float(temp.replace("temp=", "").replace("'C", "")) #Remove text and convert to float
    return temp


def cpu_protect():
    temp = temp_cpu()

    if temp >= OVERHEAT_ALERT_TEMP:
        if OVERHEAT_ALERT_BUZZER and cfg["buzzer"]:
            import buzzer
            buzzer.overheating_alarm()

        if OVERHEAT_POWEROFF and temp >= OVERHEAT_POWEROFF_TEMP:
            printf.overheating("Too hot! " + str(temp) + "°C Powering off...")
            os.system("poweroff")
            sleep(5)
            os.system("sudo poweroff")
            os.system("pkill python")

        else:
            printf.overheating("Overheating! " + str(temp) + " °C")

            ui.theme("black", "orange")
            ui.plt.title(f"CAMERA OVERHEATING! CPU: {str(temp)} °C", color="black")  # Text above preview
            ui.plt.pause(0.001)
            sleep(1)
            ui.theme("black", "red")
            ui.plt.title(f"CAMERA OVERHEATING! CPU: {str(temp)} °C", color="black")  # Text above preview
            ui.plt.pause(0.001)
