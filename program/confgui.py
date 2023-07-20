#!/usr/bin/env python3

import PySimpleGUI as sg
import sys
import os
import frametools
import numpy as np
from img.confgui import *
import dt



try:
    file_input = sys.argv[1]
except IndexError:
    file_input = ""

try:
    file_output = sys.argv[2]
except IndexError:
    file_output = ""

import config



if sys.platform.startswith('win'):
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'CvetkoFabian.ThermalCamera.ConfigManager.0.0.1')



file_version_output = 2.0

theme = "SystemDefault1"

list_sensor = ["mlx90640", "lepton35", "unknown"]
list_interpolation = ["none", "nearest", "bilinear", "bicubic", "spline16", "spline36", "hanning", "hamming", "hermite", "kaiser", "quadric", "catrom", "gaussian", "bessel", "mitchell", "sinc", "lanczos"]
list_colormap      = ["__LINEAR__", 'viridis', 'plasma', 'inferno', 'magma', 'cividis',
                      "__SEQUENTIAL__", 'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
                      "__SEQUENTIAL2__", 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink', 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper',
                      "__DIVERGING__", 'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
                      "__CYCLIC__", 'twilight', 'twilight_shifted', 'hsv',
                      "__QUALITATIVE__", 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c',
                      "__MISCELLANEOUS__", 'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet', 'turbo', 'nipy_spectral', 'gist_ncar']
list_save_image_format    = ["ps", "eps", "pdf", "pgf", "png", "raw", "rgba", "svg", "svgz", "jpg", "jpeg", "tif", "tiff"]
list_units_temperature = ["kelvin", "celsius"]



config_path_os = os.path.join(os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.environ["HOME"], ".config"))
config_path_ui = os.path.join(config_path_os, "thcam", "configmanager.conf")



def cfg_contains_raw(cfg):
        if str(cfg["frame"]) != "[]":
            return True
        else:
            return False

def load_config_ui():
    global theme
    ui_cfg = config.read(config_path_ui)

    theme = config.get(ui_cfg, "Appearance", "theme", theme)

def save_config_ui():
    cfg_ui = config.obj()
    cfg_ui.add_section("Appearance")
    cfg_ui.set("Appearance", "theme", theme)

    config.write(cfg_ui, config_path_ui)

def save_config_out(values, tab_override = None, dryrun = False):
    cfg_inp = config.get_dict(config.read(file_input))
    #print(values)

    if not check_settings(values):
        return "aborted"


    if values["colormap_reverse"]:
        colormap = values["colormap"] + "_r" # If reverse checkbox ticked, append reverse string.
    else:
        colormap = values["colormap"]

    if values["temp_range_unit"] == "kelvin":
        temp_range_min = values["temp_range_min"]
        temp_range_max = values["temp_range_max"]
    elif values["temp_range_unit"] == "celsius":
        temp_range_min = round(float(values["temp_range_min"]) + 273.15, 2)
        temp_range_max = round(float(values["temp_range_max"]) + 273.15, 2)
    else:
        sg.popup_ok("'Temp. Unit' field is invalid! Unknown unit: " + values["temp_range_unit"] + "\nAborted.", title="Write", image=img_base64_bad)
        return "aborted"

    trigger_button_pins = values["trigger_button_pins"].replace("(", "").replace(",)", "").replace(")", "")
    if trigger_button_pins[-1] == ",": # Remove trailing period to prevent crash when config file is read
        trigger_button_pins = trigger_button_pins[:-1]

    save_path = values["save_path"]
    if save_path[-1] == "/":  # Remove trailing slash.
        save_path = save_path[:-1]

    feed_path = values["feed_path"]
    if feed_path[-1] == "/":  # Remove trailing slash.
        feed_path = feed_path[:-1]

    cfg_out = config.obj()

    cfg_out.add_section("Hardware")
    cfg_out.set("Hardware", "sensor", values["sensor"])

    cfg_out.add_section("Accuracy")
    cfg_out.set("Accuracy", "emissivity", values["emissivity"])

    cfg_out.add_section("View")
    cfg_out.set("View", "unit_temperature", values["unit_temperature"])
    cfg_out.set("View", "interpolation", values["interpolation"])
    cfg_out.set("View", "colormap", colormap)
    cfg_out.set("View", "limits_enable", str(values["limits"]))
    cfg_out.set("View", "limits_x", str(values["limits_x_min"]) + ", " + str(values["limits_x_max"]))
    cfg_out.set("View", "limits_y", str(values["limits_y_max"]) + ", " + str(values["limits_y_min"])) # Tuple is flipped, cuz matpotlib i guess

    cfg_out.add_section("Temperature_Range")
    cfg_out.set("Temperature_Range", "enable", str(values["temp_range"]))
    cfg_out.set("Temperature_Range", "min", str(temp_range_min))
    cfg_out.set("Temperature_Range", "max", str(temp_range_max))
    cfg_out.set("Temperature_Range", "auto_adjust", str(values["temp_range_auto_adjust"]))

    cfg_out.add_section("Save")
    cfg_out.set("Save", "prefix", values["prefix"])
    cfg_out.set("Save", "suffix", values["suffix"])


    if tab_override == "raw" or values["tab_selected"] == "tab_raw" and tab_override != "config":
        cfg_out.add_section("File")
        cfg_out.set("File", "version", str(file_version_output))

        cfg_out.add_section("Frame")
        cfg_out.set("Frame", "timestamp", values["timestamp"])
        cfg_out.set("Frame", "frame", values["frame"].replace("\n", ""))

    elif tab_override == "config" or values["tab_selected"] == "tab_config":
        # Check if there is frame data that could be lost.
        if cfg_contains_raw(cfg_inp):
            answer = sg.popup_yes_no("Input file contains RAW data that WILL BE LOST when saving in 'Config File' mode! Write file anyways?", title="Write", image=img_base64_question)
            if answer == "No":
                return "aborted"

        cfg_out.set("Hardware", "buzzer", str(values["buzzer"]))
        cfg_out.set("Hardware", "buzzer_pin", str(values["buzzer_pin"]))
        cfg_out.set("Hardware", "led", str(values["led"]))
        cfg_out.set("Hardware", "led_pin", str(values["led_pin"]))

        cfg_out.add_section("Monitor")
        cfg_out.set("Monitor", "enable", str(values["monitor"]))
        cfg_out.set("Monitor", "invert", str(values["monitor_invert"]))
        cfg_out.set("Monitor", "max_deviations", values["monitor_max_deviations"])
        cfg_out.set("Monitor", "buzzer", str(values["monitor_buzzer"]))
        cfg_out.set("Monitor", "test_list", values["monitor_test_list"])

        cfg_out.add_section("Trigger_Buttons")
        cfg_out.set("Trigger_Buttons", "pins", trigger_button_pins)

        cfg_out.add_section("Trigger_Visual")
        cfg_out.set("Trigger_Visual", "enable", str(values["trigger_visual"]))
        cfg_out.set("Trigger_Visual", "invert", str(values["trigger_visual_invert"]))
        cfg_out.set("Trigger_Visual", "previous_frame", values["trigger_visual_previous_frame"])
        cfg_out.set("Trigger_Visual", "max_deviations", values["trigger_visual_max_deviations"])
        cfg_out.set("Trigger_Visual", "test_list", values["trigger_visual_test_list"])

        cfg_out.add_section("Trigger_Periodic")
        cfg_out.set("Trigger_Periodic", "enable", str(values["trigger_periodic"]))
        cfg_out.set("Trigger_Periodic", "interval", values["trigger_periodic_interval"])

        cfg_out.set("Save", "path", save_path)
        cfg_out.set("Save", "raw", str(values["save_raw"]))
        cfg_out.set("Save", "image", str(values["save_image"]))
        cfg_out.set("Save", "image_format", values["save_image_format"])
        cfg_out.set("Save", "buzzer", str(values["save_buzzer"]))
        cfg_out.set("Save", "led", str(values["save_led"]))

        cfg_out.add_section("Feed")
        cfg_out.set("Feed", "enable", str(values["feed"]))
        cfg_out.set("Feed", "path", values["feed_path"])
        cfg_out.set("Feed", "length", values["feed_length"])

    else:
        # The program should never be able to get here.
        print("No valid tab selected?!?!?!?!")
        raise Exception

    if values["file_output"] != "":
        if not dryrun:
            config.write(cfg_out, values["file_output"])
    else:
        if not dryrun:
            sg.popup_ok("'Output File' field is empty! File can't be written.", title="Write", image=img_base64_bad)
            return "aborted"

    return cfg_out


def check_settings(values):
    if values["tab_selected"] == "tab_config" and values["sensor"] == "unknown":
        sg.popup_ok("You have to specify a sensor when creating a config file for the thermal camera. The thermal camera program won't be able to start without knowing the sensor it has to use!", title="Sensor", image=img_base64_bad)
        return False

    if values["sensor"] not in list_sensor:
        result = sg.popup_yes_no("Not a valid sensor: " + values["sensor"] + " \n\nThis will result in the Program reading the file to crash / error out if this sensor is not supported by it! \nContinue anyways?", title="Sensor", image=img_base64_bad)
        if result == "No":
            return False

    if values["interpolation"] not in list_interpolation:
        sg.popup_ok("Not a valid interpolation method: " + values["interpolation"], title="Interpolation", image=img_base64_bad)
        return False

    if values["colormap"] not in list_colormap:
        sg.popup_ok("Not a valid colormap: " + values["colormap"], title="Colormap", image=img_base64_bad)
        return False

    return True



size_text_l = (11, None)
size_text_num = (7, None)
size_text_med = (15, None)
size_combo = (30, None)

color_button_read = ("Black", "LightBlue")
color_button_write = ("Black", "LightYellow")
color_popup_good = ("White", "DarkGreen")
color_popup_exception = ("White", "DarkRed")
font_important = (None, 10, "bold")
font_popup_help = (None, 12, "bold")



def main():
    global file_input  # If input file is invalid, it has to be cleared.

    try:
        cfg = config.get_dict(config.read(file_input))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(str(e))
        sg.popup_error("'Input File' could not be read! Is it a compatible file? \nFalling back to default settings. \n\n" + file_input + "\n\nError: " + str(e)[:1000], title="Read", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])
        print("\nError: Invalid Input File!")
        #sys.exit(2)
        file_input = ""
        cfg = config.get_dict(config.read(file_input))

    if cfg["colormap"][-2:] == "_r": # Check if last two characters are "_r" which would mean it was reversed.
        colormap_reversed = True
        colormap = cfg["colormap"][:-2] # Strip last two characters from string
    else:
        colormap_reversed = False
        colormap = cfg["colormap"]

    # Convert from Kelvin to Celsius for ease of use. Round to 2 decimal points because of float inpercision
    temp_range_min = round(float(cfg["temp_range_min"]) - 273.15, 2)
    temp_range_max = round(float(cfg["temp_range_max"]) - 273.15, 2)
    temp_range_unit = "celsius"

    frame_stringifyed = frametools.stringify(cfg["frame"]) # Convert frame data to string list
    frame_stringifyed = frame_stringifyed.replace("], ", "], \n").replace("[[", "[\n[").replace("]]", "]\n]") # Insert newlines to make list more readable

    monitor_test_list_stringifyed = frametools.stringify(cfg["monitor_test_list"])
    trigger_visual_test_list_stringifyed = frametools.stringify(cfg["trigger_visual_test_list"])

    trigger_button_pins = str(cfg["trigger_button_pins"]).replace("(", "").replace(")", "")
    if trigger_button_pins[-1] == ",": # Remove trailing period to prevent crash when config file is read
        trigger_button_pins = trigger_button_pins[:-1]

    l_config = [
                [sg.Text("Buzzer:", size=size_text_l), sg.Checkbox("enable", default=cfg["buzzer"], size=size_text_l, key="buzzer"), sg.Text("GPIO pin:", size_text_l), sg.Input(cfg["buzzer_pin"], size=size_text_num, key="buzzer_pin"), sg.Push(), sg.Button("ⓘ", key="buzzer_help")],
                [sg.Text("LED:", size=size_text_l), sg.Checkbox("enable", default=cfg["led"], size=size_text_l, key="led"), sg.Text("GPIO pin:", size_text_l), sg.Input(cfg["led_pin"], size=size_text_num, key="led_pin"), sg.Push(), sg.Button("ⓘ", key="led_help")],
                [sg.HorizontalSeparator()],
                [sg.Text("Monitor:", size=size_text_l), sg.Checkbox("enable", default=cfg["monitor"], size=size_text_l, key="monitor"), sg.Checkbox("invert", default=cfg["monitor_invert"], key="monitor_invert"), sg.Push(), sg.Button("ⓘ", key="monitor_help")],
                [sg.Text("max. Deviations:", size=size_text_l), sg.Input(cfg["monitor_max_deviations"], size=size_text_num, key="monitor_max_deviations"), sg.Text("%", size=(5, None))],
                [sg.Text("Test-List:", size=size_text_l), sg.Input(monitor_test_list_stringifyed, key="monitor_test_list", size=(40, None)), sg.Push(), sg.Button("View", key="monitor_test_list_view"), sg.Button("Edit", key="monitor_test_list_edit")],
                [sg.Text("Buzzer Alarm:", size=size_text_l), sg.Checkbox("enable", default=cfg["monitor_buzzer"], key="monitor_buzzer")],
                [sg.HorizontalSeparator()],
                [sg.Text("Trigger Button(s):", size=(14, None)), sg.Text("GPIO pin(s):", size=size_text_l), sg.Input(trigger_button_pins, size=size_text_med, key="trigger_button_pins"), sg.Push(), sg.Button("ⓘ", key="trigger_button_help")],
                [sg.HorizontalSeparator()],
                [sg.Text("Visual Trigger:", size=size_text_l), sg.Checkbox("enable", default=cfg["trigger_visual"], size=size_text_l, key="trigger_visual"), sg.Checkbox("invert", default=cfg["trigger_visual_invert"], key="trigger_visual_invert"), sg.Push(), sg.Button("ⓘ", key="trigger_visual_help")],
                [sg.Text("max. Deviations:", size=size_text_l), sg.Input(cfg["trigger_visual_max_deviations"], size=size_text_num, key="trigger_visual_max_deviations"), sg.Text("%", size=(6, None)), sg.Text("Previous Frames:", size=size_text_l), sg.Input(cfg["trigger_visual_previous_frame"], size=size_text_num, key="trigger_visual_previous_frame")],
                [],
                [sg.Text("Test-List:", size=size_text_l), sg.Input(trigger_visual_test_list_stringifyed, key="trigger_visual_test_list", size=(40, None)), sg.Push(), sg.Button("View", key="trigger_visual_test_list_view"), sg.Button("Edit", key="trigger_visual_test_list_edit")],
                [sg.HorizontalSeparator()],
                [sg.Text("Timed Trigger:", size_text_l), sg.Checkbox("enable", default=cfg["trigger_periodic"], size=size_text_l, key="trigger_periodic"), sg.Input(cfg["trigger_periodic_interval"], size=size_text_med, key="trigger_periodic_interval"), sg.Text("s"), sg.Push(), sg.Button("ⓘ", key="trigger_periodic_help")],
                [sg.HorizontalSeparator()],
                [sg.Text("Save Files:", size=size_text_l), sg.Checkbox("RAW File", size=size_text_l, default=cfg["save_raw"], key="save_raw"), sg.Checkbox("Image File:", size=(8, None), default=cfg["save_image"], key="save_image"), sg.Combo(list_save_image_format, default_value=cfg["save_image_format"], size=size_text_num, key="save_image_format"), sg.Push(), sg.Button("ⓘ", key="save_help")],
                [sg.Text("Save Path:", size=size_text_l), sg.Input(cfg["save_path"], key="save_path"), sg.FileSaveAs("Browse")],
                [sg.Text("Buzz on save:", size=size_text_l), sg.Checkbox("enable", default=cfg["save_buzzer"], size=size_text_l, key="save_buzzer"), sg.Text("LED on save:", size_text_l), sg.Checkbox("enable", default=cfg["save_led"], size=size_text_l, key="save_led")],
                [sg.HorizontalSeparator()],
                [sg.Text("Feed:", size=size_text_l), sg.Checkbox("enable", default=cfg["feed"], size=size_text_l, key="feed"), sg.Text("length:", size=size_text_l), sg.Input(cfg["feed_length"], size=size_text_num, key="feed_length"), sg.Push(), sg.Button("ⓘ", key="feed_help")],
                [sg.Text("Feed Path:", size=size_text_l), sg.Input(cfg["feed_path"], key="feed_path"), sg.FileSaveAs("Browse")],
                ]

    l_rawfile = [
                [sg.Text("File version:", size=size_text_l), sg.Text("input:    " + str(cfg["version"]), size=(14, None)), sg.Text("output:    " + str(file_version_output), size=(14, None))],
                [sg.Text("Timestamp:", size=size_text_l), sg.Input(cfg["timestamp"], size=size_text_med, key="timestamp"), sg.Text("  " + dt.iso(cfg["timestamp"]), key="datetime_iso"), sg.Push(), sg.Button("ⓘ", key="timestamp_help")],
                [sg.Text("Frame data:", size=size_text_l), sg.Button("View", key="frame_view"), sg.Push(), sg.Button("ⓘ", key="frame_help")],
                [sg.Multiline(frame_stringifyed, size=(65, 27), key="frame")],
                ]

    l_main =    [
                [sg.Text("Sensor:", size=size_text_l), sg.Combo(list_sensor, default_value=cfg["sensor"], key="sensor", size=size_combo)],
                [sg.Text("Emissivity:", size=size_text_l), sg.Slider((0.01, 1), default_value=cfg["emissivity"], resolution=0.01, orientation="horizontal", disable_number_display=True, key="emissivity_slider", enable_events=True), sg.Input(cfg["emissivity"], key="emissivity", size=(4, None))],
                [sg.HorizontalSeparator()],
                [sg.Text("Temp. Unit:", size=size_text_l), sg.Combo(list_units_temperature, key="unit_temperature", default_value=cfg["unit_temperature"])],
                [sg.Text("Interpolation:", size=size_text_l), sg.Combo(list_interpolation, key="interpolation", default_value=cfg["interpolation"], size=size_combo), sg.Push(), sg.Button("ⓘ", key="interpolation_help")],
                [sg.Text("Colormap:", size=size_text_l), sg.Combo(list_colormap, key="colormap", default_value=colormap, size=size_combo, enable_events=True), sg.Checkbox("reverse", default=colormap_reversed, key="colormap_reverse"), sg.Push(), sg.Button("ⓘ", key="colormap_help")],
                [sg.HorizontalSeparator()],
                [sg.Text("Enable Limts:", size=size_text_l), sg.Checkbox("enable", default=cfg["limits"], key="limits"), sg.Push(), sg.Button("ⓘ", key="limits_help")],
                [sg.Text("x (horizontal):", size=size_text_l), sg.Text("min."), sg.Input(cfg["limits_x"][0], size=size_text_num, key="limits_x_min"), sg.Text("max."), sg.Input(cfg["limits_x"][1], size=size_text_num, key="limits_x_max")],
                [sg.Text("y (vertical):", size=size_text_l), sg.Text("min."), sg.Input(cfg["limits_y"][1], size=size_text_num, key="limits_y_min"), sg.Text("max."), sg.Input(cfg["limits_y"][0], size=size_text_num, key="limits_y_max")],
                [sg.HorizontalSeparator()],
                [sg.Text("Temp. Range:", size=size_text_l), sg.Checkbox("enable", default=cfg["temp_range"], key="temp_range"), sg.Checkbox("autoadjust", default=cfg["temp_range_autoadjust"], key="temp_range_auto_adjust"), sg.Push(), sg.Button("ⓘ", key="temp_range_help")],
                [sg.Text("Temp. Range:", size=size_text_l), sg.Text("min."), sg.Input(temp_range_min, size=size_text_num, key="temp_range_min"), sg.Text("max."), sg.Input(temp_range_max, size=size_text_num, key="temp_range_max"), sg.Combo(list_units_temperature, default_value=temp_range_unit, key="temp_range_unit")],
                [sg.HorizontalSeparator()],
                [sg.Text("Name Prefix:", size=size_text_l), sg.Input(cfg["save_prefix"], size=(15, None), key="prefix"), sg.Text("Name Suffix:", size=size_text_l), sg.Input(cfg["save_suffix"], size=(15, None), key="suffix"), sg.Push(), sg.Button("ⓘ", key="prefix_suffix_help")],
                [sg.HorizontalSeparator()],
                [sg.TabGroup([[sg.Tab("Camera Config File", l_config, key="tab_config")],
                            [sg.Tab("RAW File", l_rawfile, key="tab_raw")],
                            ], tab_location="topleft", enable_events=True, key="tab_selected")],
                [sg.HorizontalSeparator()],
                [sg.Text("Input File:", size=size_text_l, font=font_important), sg.Input(file_input, key="file_input", background_color=color_button_read[1], text_color=color_button_read[0]), sg.FileBrowse(button_color=color_button_read)],
                [sg.Text("Output File:", size=size_text_l, font=font_important), sg.Input(file_output, key="file_output", background_color=color_button_write[1], text_color=color_button_write[0]), sg.FileSaveAs("Browse", button_color=color_button_write)],
                [sg.Button("Write to Output File", key="Write", button_color=color_button_write, font=font_important), sg.Button("Read from Input File", key="Read", button_color=color_button_read, font=font_important), sg.Push(), sg.Text("", key="theme_text", size=(14, None)), sg.Button("シ", key="theme", tooltip="Apply random theme"), sg.Button("Quit")],
                ]

    return sg.Window("Thermal Camera Config Manager", l_main, icon=img_base64_icon)

def roi_selector_row(i, x_min = "", y_min = "", x_max = "", y_max = "", temp_min = "", temp_max = ""):
    l_row =  [
                [sg.Text(str(i) + ":", size=(2, None)), sg.Input(x_min, size=size_text_num, key=("area_x_min", i)), sg.Input(y_min, size=size_text_num, key=("area_y_min", i)), sg.Input(x_max, size=size_text_num, key=("area_x_max", i)), sg.Input(y_max, size=size_text_num, key=("area_y_max", i)), sg.Input(temp_min, size=size_text_num, key=("area_temp_min", i)), sg.Input(temp_max, size=size_text_num, key=("area_temp_max", i))],
                ]

    return l_row



def _roi_selector():
    size_text_num_col = (6, None)

    roi_unit = "celsius"

    l_row = [
                [sg.Text("", size=(2, None)), sg.Text(" Area:", size=(30, None)), sg.Text("Temp:")],
                [sg.Text("", size=(2, None)), sg.Text("  x min.", size=size_text_num_col), sg.Text("  y min.", size=size_text_num_col), sg.Text("  x max.", size=size_text_num_col), sg.Text("  y max.", size=(size_text_num_col)), sg.VerticalSeparator(), sg.Text(" min.", size=size_text_num_col), sg.Text(" max.", size=(7, None))],
    ]

    l_main =    [
                [sg.Column(l_row, key='row')],
                [sg.Button("Add row", key="add_row"), sg.Text(size=(23, None)), sg.Combo(list_units_temperature, default_value=roi_unit, key="roi_unit_temperature", size=(14, None))],
                [sg.HorizontalSeparator()],
                [sg.Button("Apply and return", key="return"), sg.Button("Read", key="read"), sg.Push(), sg.Button("ⓘ", key="roi_selector_help"), sg.Button("Discard", key="discard")],
                ]

    return sg.Window("Thermal Camera ROI Editor", l_main, icon=img_base64_icon)

def roi_selector(input_list = []):
    window_as = _roi_selector()
    area_row_i = 0
    while True:
        event_as, values_as = window_as.read(timeout=100)

        if event_as == sg.WIN_CLOSED or event_as == "discard":
            window_as.close()
            break

        if event_as == "read":
            rows = range(np.shape(input_list)[0])
            for row in rows:
                y_min = input_list[row][0]
                x_min = input_list[row][1]
                y_max = input_list[row][2]
                x_max = input_list[row][3]

                if values_as["roi_unit_temperature"] == "kelvin":
                    temp_min = float(input_list[row][4])
                    temp_max = float(input_list[row][5])
                elif values_as["roi_unit_temperature"] == "celsius":
                    temp_min = round(float(input_list[row][4]) - 273.15, 2)
                    temp_max = round(float(input_list[row][5]) - 273.15, 2)
                else:
                    sg.popup_ok("Invalid temperature unit!", title="ROI", image=img_base64_bad)
                    return None

                window_as.extend_layout(window_as["row"], roi_selector_row(area_row_i, x_min = x_min, y_min = y_min, x_max = x_max, y_max = y_max, temp_min = temp_min, temp_max = temp_max))
                area_row_i += 1

        if event_as == "add_row":
            window_as.extend_layout(window_as["row"], roi_selector_row(area_row_i))
            area_row_i += 1

        if event_as == "return":
            list_area = []
            for i in range(area_row_i):
                try:
                    if values_as["roi_unit_temperature"] == "kelvin":
                        temp_min = float(values_as["area_temp_min", i])
                        temp_max = float(values_as["area_temp_max", i])
                    elif values_as["roi_unit_temperature"] == "celsius":
                        temp_min = round(float(values_as["area_temp_min", i]) + 273.15, 2)
                        temp_max = round(float(values_as["area_temp_max", i]) + 273.15, 2)
                    else:
                        sg.popup_ok("Invalid temperature unit!",title="ROI", image=img_base64_bad)
                        return None

                    # Convert to int and remove decimals to prevent error when 4 some stupid reason 0.0 sneaks in there.
                    y_min = int(values_as["area_y_min", i].split(".")[0])
                    x_min = int(values_as["area_x_min", i].split(".")[0])
                    y_max = int(values_as["area_y_max", i].split(".")[0])
                    x_max = int(values_as["area_x_max", i].split(".")[0])

                    list_area_row = []
                    list_area_row.append(y_min)
                    list_area_row.append(x_min)
                    list_area_row.append(y_max)
                    list_area_row.append(x_max)
                    list_area_row.append(temp_min)
                    list_area_row.append(temp_max)

                    list_area.append(list_area_row)
                except ValueError as e:
                    import traceback

                    print("Row " + str(i) + " in Pixels contains invalid entries! It has been skipped.")
                    traceback.print_exc()
                    print(str(e))
                    sg.popup_error("Row " + str(i) + " in Pixels contains invalid entries! It has been skipped. \n\nError:" + str(e)[:1000], title="ROI", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

            list_area_stringifyed = frametools.stringify(np.array(list_area))
            window_as.close()

            return list_area_stringifyed

        # Colormap help popup
        if event_as == "roi_selector_help":
            sg.popup_ok("Pixel coordinates must be whole numbers. \nTemperatures can have up to 2 decimals after the separator.", title="ROI", image=img_base64_test_list_editor, font=font_popup_help)

    return None

def viewer_raw(cfg):
    try:
        import read
        read.read(cfg)
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(str(e))
        sg.popup_error("Failed to start viewer! \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

# Cycle through multiple help pages
def help_multi(pages, title = "Help"):
    for idx, page in enumerate(pages):
        sg.popup_ok(page[1], title=title + " (" + str(idx + 1) + "/" + str(len(pages)) + ")", image=page[0], font=font_popup_help)

def check_input(value, check):
    if check == "isdecimal":
        if not value.isdecimal():
            sg.popup_ok("Value must only contain characters '0'-'9'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input", image=img_base64_bad)
            return False
    if check == "isdecimal_percent":
        try:
            if not value.isdecimal():
                raise Exception
            elif int(value) > 100:
                raise Exception
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9' and be between '0'-'100'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input", image=img_base64_bad)
            return False
    elif check == "float":
        try:
            float(value)
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9', '-' and '.'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False
    elif check == "float_positive":
        try:
            float(value)
            if "-" in value:
                raise Exception
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9' and '.'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False
    elif check == "float_celsius":
        try:
            value_float = float(value)
            if value_float < -273.15:
                raise Exception
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9', '-', '.' and not be less than '-273.15'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False
    elif check == "int":
        try:
            int(value)
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9' and '-'! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False
    elif check == "tuple_positive":
        try:
            tuple(map(int, (value.split(","))))
            if "-" in value:
                raise Exception
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9', ',' and ' '! It must also not end with a period ','! \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False
    elif check == "array_noletters":
        try:
            np.array(eval(value))
            if value.upper().isupper():
                raise Exception
        except Exception:
            sg.popup_ok("Value must only contain characters '0'-'9', ',', '[', ']'and ''! It also must be a valid list and all sections have to be the same length! \n[[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]] would be valid. \n[[1, 2, 3, 4, 5, 6], [1, 2, 3, 4]] would be invalid because the secions are not the same length. \n\nEntered value is: " + str(value[:1000]), title="Invalid Input",image=img_base64_bad)
            return False

    return True



load_config_ui()
sg.theme(theme)
sg.SetOptions(font=(None, 10), element_padding=(3, 2))
window = main()


# Select RAW tab when raw data in file
event, values = window.read()
if cfg_contains_raw(config.get_dict(config.read(file_input))):
    window["tab_raw"].select()

window.BringToFront()

while True:
    event, values = window.read(timeout=100)
    config.get_dict(config.read(file_input))

    if event == sg.WIN_CLOSED or event == "Quit":  # if user closes window or clicks cancel
        # print(values)
        break

    # Read values from config and reset window
    if event == "Read":
        if values["file_input"] == "":
            sg.popup_ok("'Input File' field is empty! Falling back to default settings.", title="Read", image=img_base64_info)

        file_input = values["file_input"]
        file_output = values["file_output"]

        # Re-open window
        window.close()
        window = main()
        event, values = window.read(timeout=100)

        # Select RAW tab when raw data in file
        if cfg_contains_raw(config.get_dict(config.read(file_input))):
            window["tab_raw"].select()

    if event == "Write":
        file_output = values["file_output"] # Not really needed, but it keeps the value stored when window gets refreshed.

        result = save_config_out(values)
        if result != "aborted":
            sg.popup_ok("'Output File' was written. \n\n" + values["file_output"], title="Write", image=img_base64_good, background_color=color_popup_good[1], text_color=color_popup_good[0])

    # Cycle through themes randomly
    if event == "theme":
        import random

        while True:
            theme = random.choice(sg.theme_list())
            if theme != "Default": # Default shows a message in output to use DefaultNoMoreNagging. Sooooo lets just not use that :-P
                break
        # print(theme)
        window.close()
        sg.theme(theme)
        window = main()
        event, values = window.read(timeout=100)
        window.Element("theme_text").Update(theme)
        save_config_ui()

    # Update Input and Slider when either one is changed and check for valid input.
    window["emissivity"].bind("<Return>", "_Enter")
    window["emissivity"].bind("<FocusOut>", "_FocusOut")
    window["emissivity_slider"].bind("<ButtonRelease-1>", "_Slide")
    if event == "emissivity" + "_Enter" or event == "emissivity" + "_FocusOut":
        try:
            if float(values["emissivity"]) >= 0.01 and float(values["emissivity"]) <= 1:
                window.Element("emissivity_slider").Update(values["emissivity"])
            else:
                window.Element("emissivity").Update(values["emissivity_slider"])
                sg.popup_ok("Emissivity value must be between 0.01 and 1! Entered value is " + str(values["emissivity"] + "."), title="Emissivity", image=img_base64_bad)
        except ValueError:
            window.Element("emissivity").Update(values["emissivity_slider"])
            sg.popup_ok("Emissivity value must be numerical! \n\nEntered value is " + str(values["emissivity"] + "."), title="Emissivity", image=img_base64_bad)
    if event == "emissivity_slider" + "_Slide":
        window.Element("emissivity").Update(values["emissivity_slider"])

    if event == "colormap":
        if values["colormap"].startswith("__") and values["colormap"].endswith("__"):
            sg.popup_ok("__CATEGORY__ entries aren't valid colormaps!", title="Colormap", image=img_base64_bad)
            window.Element("colormap").Update(config.get_dict(config.read(file_input))["colormap"])


    window["timestamp"].bind("<Return>", "_Enter")
    window["timestamp"].bind("<FocusOut>", "_FocusOut")
    if event == "timestamp" + "_Enter" or event == "timestamp" + "_FocusOut":
        if check_input(values["timestamp"], "isdecimal"):
            try:
                window.Element("datetime_iso").Update("  " + dt.iso(int(values["timestamp"])))
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(str(e))
                sg.popup_error("Failed to update datetime with timestamp! \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

                window.Element("timestamp").Update(0)
                window.Element("datetime_iso").Update("  " + dt.iso(0))
        else:
            window.Element("timestamp").Update(0)
            window.Element("datetime_iso").Update("  " + dt.iso(0))

    # Check if Limits and GPIO Buzzer values are o.k.
    for field in ("limits_x_min", "limits_y_min", "limits_x_max", "limits_y_max", "buzzer_pin", "led_pin", "trigger_visual_previous_frame", "trigger_periodic_interval", "feed_length"):
        window[field].bind("<Return>", "_Enter")
        window[field].bind("<FocusOut>", "_FocusOut")
        if event == field + "_Enter" or event == field + "_FocusOut":
            if not check_input(values[field], "isdecimal"):
                window.Element(field).Update(0)

    # Check if Temp. Range values are o.k.
    for field in ("temp_range_min", "temp_range_max"):
        window[field].bind("<Return>", "_Enter")
        window[field].bind("<FocusOut>", "_FocusOut")
        if event == field + "_Enter" or event == field + "_FocusOut":
            if values["temp_range_unit"] == "kelvin":
                if not check_input(values[field], "float_positive"):
                    window.Element(field).Update(0)
            elif values["temp_range_unit"] == "celsius":
                if not check_input(values[field], "float_celsius"):
                    window.Element(field).Update(0)
            else:
                sg.popup_ok("Unknown temperature unit: " + values["temp_range_unit"],title="Temperature Range", image=img_base64_bad)

    # Check if GPIO Button values are o.k.
    for field in ("trigger_button_pins", ):
        window[field].bind("<Return>", "_Enter")
        window[field].bind("<FocusOut>", "_FocusOut")
        if event == field + "_Enter" or event == field + "_FocusOut":
            if not check_input(values[field], "tuple_positive"):
                window.Element(field).Update(0)

    # Check if Deviation percent values are o.k.
    for field in ("monitor_max_deviations", "trigger_visual_max_deviations"):
        window[field].bind("<Return>", "_Enter")
        window[field].bind("<FocusOut>", "_FocusOut")
        if event == field + "_Enter" or event == field + "_FocusOut":
            if not check_input(values[field], "isdecimal_percent"):
                window.Element(field).Update(0)

    # Check if Deviation percent values are o.k.
    for field in ("monitor_test_list", "trigger_visual_test_list", "frame"):
        window[field].bind("<Return>", "_Enter")
        window[field].bind("<FocusOut>", "_FocusOut")
        if event == field + "_Enter" or event == field + "_FocusOut":
            if not check_input(values[field], "array_noletters"):
                window.Element(field).Update("[]")

    if event == "frame_view":
        window.Disable()

        if values["frame"] == "[]" or values["frame"] == "":
            sg.popup_ok("No data in 'frame' field! Have you loaded a RAW input file?", title="View Image", image=img_base64_bad)
        else:
            dryrun_frame = save_config_out(values, tab_override="raw", dryrun=True)
            if not dryrun_frame == "aborted":  # Prevent crash if dryrun was aborted.
                try:
                    dryrun_frame_dict = config.get_dict(dryrun_frame)
                    viewer_raw(dryrun_frame_dict)
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(str(e))
                    sg.popup_error("Failed to start Viewer! \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

        window.Enable()
        window.BringToFront()

    if event == "monitor_test_list_edit":
        window.Disable()

        if values["monitor_test_list"] == "": # Catch empty field
            roi = roi_selector()
        else:
            try:
                roi = roi_selector(eval(values["monitor_test_list"]))
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(str(e))
                sg.popup_error("Error occurred in the ROI editor! This is probably caused by an invalid entry in the 'Test-List' field. \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

                answer = sg.popup_yes_no("Should I empty the 'Test-List' field for you?", title="ROI", image=img_base64_question)
                if answer == "Yes":
                    window.Element("monitor_test_list").Update("[]")

                roi = None

        if roi != None:
            window.Element("monitor_test_list").Update(roi)

        window.Enable()
        window.BringToFront()

    if event == "trigger_visual_test_list_edit":
        window.Disable()

        if values["trigger_visual_test_list"] == "": # Catch empty field
            roi = roi_selector()
        else:
            try:
                roi = roi_selector(eval(values["trigger_visual_test_list"]))
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(str(e))
                sg.popup_error("Error occurred in the ROI editor! This is probably caused by an invalid entry in the 'Test-List' field. \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

                answer = sg.popup_yes_no("Should I empty the 'Test-List' field for you?", title="ROI",
                                 image=img_base64_question)
                if answer == "Yes":
                    window.Element("trigger_visual_test_list").Update("[]")

                roi = None

        if roi != None:
            window.Element("trigger_visual_test_list").Update(roi)

        window.Enable()
        window.BringToFront()

    if event == "monitor_test_list_view":
        window.Disable()

        if values["monitor_test_list"] == "[]" or values["monitor_test_list"] == "":
            sg.popup_ok("No data in 'Test-List' field!", title="View", image=img_base64_bad)
        else:
            view_file_path = sg.popup_get_file("Select a RAW File to view:")
            if view_file_path != None: # Only proceed if not canceled.
                try:
                    view_cfg = config.get_dict(config.read(view_file_path))

                    # Add test list to cfg
                    if values["sensor"] == view_cfg["sensor"]:
                        test_list_str = values["monitor_test_list"]
                        test_list = np.array(eval(test_list_str))

                        overlay = frametools.overlay_roi(cfg = view_cfg, test_list = test_list)

                        view_cfg.update({"overlay": True})
                        view_cfg.update({"overlay_data": overlay})

                        viewer_raw(view_cfg)
                    else:
                        sg.popup_ok("Sensor specified in the input field does not match the sensor used to capture the RAW file! \n\nSpecified: " + str(values["sensor"] + " \nRAW File: " + view_cfg["sensor"]), title="View", image=img_base64_bad)
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(str(e))
                    sg.popup_error("Failed to start viewer! \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

        window.Enable()
        window.BringToFront()

    if event == "trigger_visual_test_list_view":
        window.Disable()

        if values["trigger_visual_test_list"] == "[]" or values["trigger_visual_test_list"] == "":
            sg.popup_ok("No data in 'Test-List' field!", title="View", image=img_base64_bad)
        else:
            view_file_path = sg.popup_get_file("Select a RAW File to view:")
            if view_file_path != None: # Only proceed if not canceled.
                try:
                    view_cfg = config.get_dict(config.read(view_file_path))

                    # Add test list to cfg
                    if values["sensor"] == view_cfg["sensor"]:
                        test_list_str = values["trigger_visual_test_list"]
                        test_list = np.array(eval(test_list_str))

                        overlay = frametools.overlay_roi(cfg = view_cfg, test_list = test_list)

                        view_cfg.update({"overlay": True})
                        view_cfg.update({"overlay_data": overlay})

                        viewer_raw(view_cfg)
                    else:
                        sg.popup_ok("Sensor specified in the input field does not match the sensor used to capture the RAW file! \n\nSpecified: " + str(values["sensor"] + " \nRAW File: " + view_cfg["sensor"]), title="View", image=img_base64_bad)
                except Exception as e:
                    import traceback

                    traceback.print_exc()
                    print(str(e))
                    sg.popup_error("Failed to start viewer! \n\nError: " + str(e)[:1000], title="View", image=img_base64_exception, background_color=color_popup_exception[1], text_color=color_popup_exception[0])

        window.Enable()
        window.BringToFront()


    # Interpolation help popup
    if event == "interpolation_help":
        sg.popup_ok("", title="Interpolation methods", image=img_base64_interpolation, font=font_popup_help)

    # Colormap help popup
    if event == "colormap_help":
        sg.popup_ok("", title="Colormaps", image=img_base64_colormaps, font=font_popup_help)

    if event == "buzzer_help":
        sg.popup_ok("Use the PWM pins when possible.", title="GPIO Pinout", image=img_base64_gpio_pinout, font=font_popup_help)

    if event == "led_help":
        sg.popup_ok("Always use a appropriate series resistor when powering LEDs from the GPIO pins!!! Not doing so can damage the Raspberry Pi.", title="GPIO Pinout", image=img_base64_gpio_pinout, text_color="Red", font=font_popup_help)

    if event == "trigger_button_help":
        sg.popup_ok("Multiple pins can be entered by separating them with a comma followed by a space: '26, 19, 13, 6, ...' \n\nIf you only use one pin just enter the number by itself: '12'", title="GPIO Pinout", image=img_base64_gpio_pinout, font=font_popup_help)

    if event == "limits_help":
        help_multi(img_base64_limits, "Limits")

    if event == "temp_range_help":
        help_multi(img_base64_temp_range, "Temperature Range")

    if event == "prefix_suffix_help":
        sg.popup_ok("", title="Prefix & Suffix", image=img_base64_prefix_suffix, font=font_popup_help)

    if event == "feed_help":
        sg.popup_ok("Important!: The directory path has to be valid on the device that the Thermal Camera program runs on! Paths vary between devices! Also keep in mind that Windows uses back slashes '\\' while most other operating systems use forward slashes '/' and don't have drive letters... \n\nThis feature saves a sepperate copy of each capture into a folder. The copied images are automatically renamed numerically. '0' is the latest capture. A simple website (for example) can then always show the latest captures by periodically refreshing.", title="Feed", image=img_base64_feed, font=font_popup_help)

    if event == "save_help":
        sg.popup_ok("Important!: The directory path has to be valid on the device that the Thermal Camera program runs on! Paths vary between devices! Also keep in mind that Windows uses back slashes '\\' while most other operating systems use forward slashes '/' and don't have drive letters...", title="Save", image=img_base64_save, font=font_popup_help)

    if event == "trigger_periodic_help":
        sg.popup_ok("Trigger a save every 'n' seconds", title="Periodic Trigger", image=img_base64_wait, font=font_popup_help)

    if event == "monitor_help":
        sg.popup_ok("This feature checks if the temperatures the camera measures are in the specified tolerance or not. The Thermal Camera program turns red if the conditions are not met. Optionally a led and/or acoustic buzzer-alarm can be activated. \n\nDetails on how to specify the regions of interest and their tolerances can be found in the Help button of the \nROI Editor ( Test-List: => [ Edit ] => [ i ] ). \n\nWith the 'max. Deviations' option you can specify how many percent of the monitored area are allowed out of tolerance. \n\nThe 'Invert' option reverses the result. If the mesaured temperatures are NOT in the specified range, that would be ok.", title="Monitor (1/2)", image=img_base64_test_list, font=font_popup_help)
        sg.popup_ok(
            "Example of the program turning red when the conditions are not met.",
            title="Monitor (2/2)", image=img_base64_temp_alarm, font=font_popup_help)

    if event == "trigger_visual_help":
        sg.popup_ok("This feature triggers a save if the temperatures the camera measures are in the specified range. \n\nDetails on how to specify the regions of interest and their tolerances can be found in the Help button of the \nROI Editor ( Test-List: => [ Edit ] => [ i ] ). \n\nWith the 'max. Deviations' option you can specify how many percent of the monitored area are allowed out of range to still trigger a save. \n\nThe 'Invert' option reverses the conditions to trigger a save. If the mesaured temperatures are NOT in the specified range, that would trigger a save.", title="Visual Trigger", image=img_base64_test_list, font=font_popup_help)

    if event == "frame_help":
        help_multi(img_base64_frame, "Frame")

    if event == "timestamp_help":
        sg.popup_ok("The timestamp is saved as 'unix time'. \nIt's the amount of seconds that have passed since 1970-01-01 00:00:00 UTC (not counting leap seconds).", title="Timestamp", image=img_base64_wait, font=font_popup_help)


window.close()