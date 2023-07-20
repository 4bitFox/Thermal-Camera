import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import use as use_backend, get_backend
import frametools
import config
import dt
import numpy as np
import sys


#Appearance
COLOR_BG = "black"
COLOR_FG = "white"
COLOR_TEMP_ALARM = "red"

fig = None
cbar = None
therm1 = None

def init(cfg = config.get_dict()):
    global fig
    global cbar
    global therm1

    backend_raspbian = "GTK3Agg"
    backend_windows = "TkAgg"

    backend = get_backend()

    if backend != backend_raspbian and backend != backend_windows:
        try:
            use_backend(backend_raspbian)
        except:
            try:
                use_backend(backend_windows)
            except:
                sys.exit("Unsupported backend. " + backend_raspbian + " and " + backend_windows + " are supported.")


    if str(cfg["frame"]) == "[]": # If frame in config is empty, we know we are running as a camera.
        UI_MODE = "camera"
    else: # Otherwise RAW file got loaded.
        UI_MODE = "viewer"


    interpolation =  cfg["interpolation"]
    colormap = cfg["colormap"]
    fullscreen = False

    #Window parameters
    if UI_MODE == "camera": # Give window generic name in camera mode
        TITLE = "Thermal Camera"
    else: # Rawfile detected. Give the Window a name with the date. Comes in handy when you need to export an image from the RAW viever.
        TITLE = cfg["save_prefix"] + dt.simple(cfg["timestamp"]) + cfg["save_suffix"]
    WINDOW_W = 800
    WINDOW_H = 480
    WINDOW_POS_X = -2
    WINDOW_POS_Y = -30
    SPACE_L = 0.05
    SPACE_B = 0.025
    SPACE_R = 0.98
    SPACE_T = 0.935


    plt.rcParams["toolbar"] = "toolbar2" # None, toolbar2, toolmanager (toolmanager flickers, so I'm using toolbar2)
    plt.ion()  # Interactive plotting
    fig, ax = plt.subplots(figsize=(12, 7))  # Subplots
    fig.canvas.manager.set_window_title(TITLE)  # Window title
    # Remove toolbar in Raspbian, but keep in Windows
    if UI_MODE == "camera": # In camera mode hide toolbar
        # Raspbian
        if backend == backend_raspbian:
            fig.canvas.manager.toolbar.hide()  # Hide toolbar
    else: # Viewer
        #Windows
        if backend == backend_windows:
            fig.canvas.manager.toolbar.children["!button4"].pack_forget() # Remove Adjust Subplots button (toolbar2 specific)
    fig.subplots_adjust(left=SPACE_L, bottom=SPACE_B, right=SPACE_R, top=SPACE_T)  # Adjust space to border
    plt.xticks([])  # Hide xticks
    plt.yticks([])  # Hide yticks
    if fullscreen:
        fig.canvas.manager.full_screen_toggle()  # Fullscreen
    else:
        if backend == backend_raspbian:
            # Raspbian
            fig.canvas.manager.window.move(WINDOW_POS_X, WINDOW_POS_Y)  # Move window
            fig.canvas.manager.window.resize(WINDOW_W, WINDOW_H)  # Resize to fit screen
        elif backend == backend_windows:
            # Windows
            mgr = plt.get_current_fig_manager()
            mgr.resize(WINDOW_W, WINDOW_H)



    # Preview and Tepmerature bar
    therm1 = ax.imshow(frametools.empty(cfg = cfg), interpolation=interpolation, cmap=colormap) # Create initial imshow plot. Has to get resolution right for correct aspect ratio.

    if "overlay" in cfg and "overlay_data" in cfg:
        if cfg["overlay"]:
            overlay_data = np.ma.masked_values(cfg["overlay_data"], -1) # Mask to make -1 transparent

            overlay1 = ax.imshow(overlay_data, interpolation="none", cmap="bwr", alpha=0.5)


    cbar = fig.colorbar(therm1)  # Colorbar for temps

    theme(COLOR_FG, COLOR_BG, cfg = cfg)



def refresh(frame, unix, cfg = config.get_dict()):
    unit_temperature_cfg = cfg["unit_temperature"]

    temp_range = cfg["temp_range"]
    temp_range_min = cfg["temp_range_min"]
    temp_range_max = cfg["temp_range_max"]
    auto_adjust_tempbar = cfg["temp_range_autoadjust"]

    if unit_temperature_cfg == "kelvin":
        unit_temperature = "K"
    elif unit_temperature_cfg == "celsius":
        unit_temperature = "°C"
        temp_range_min -= 273.15
        temp_range_max -= 273.15
        frame = frame.copy() - 273.15 # Convert K to °C

    else:
        print("Unsupported unit for temperature. Use 'kelvin', 'celsius'")
        sys.exit(4)
    therm1.set_data(frame)  # update view

    temp_min = np.min(frame)  # get min temperature
    temp_max = np.max(frame)  # get max temperature
    temp_avg = np.average(frame) # get average temperature

    if temp_range:
        # If Temperatures don't need to be clipped, set tempbar to the highest temp.
        if auto_adjust_tempbar:
            if temp_min <= temp_range_min:
                tempbar_min = temp_range_min
            else:
                tempbar_min = temp_min

            if temp_max >= temp_range_max:
                tempbar_max = temp_range_max
            else:
                tempbar_max = temp_max

        # Else set to specified Temp Range
        else:
            tempbar_min = temp_range_min
            tempbar_max = temp_range_max

    # Else set limits to min and max measured temp
    else:
        tempbar_min = temp_min
        tempbar_max = temp_max


    therm1.set_clim(vmin=tempbar_min, vmax=tempbar_max)  # set bounds
    cbar.update_normal(therm1)  # update colorbar bounds

    ticks_min = 5
    ticks_max = 10
    cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(ticks_max, min_n_ticks=ticks_min)) # set max and min amount of temperature ticks

    # Limit X, Y to e.g. zoom in on picture
    if cfg["limits"]:
        plt.xlim(cfg["limits_x"][0], cfg["limits_x"][1])
        plt.ylim(cfg["limits_y"][0], cfg["limits_y"][1])



    # Text above view. Max, Avg, Min
    if not temp_range or temp_min >= temp_range_min and temp_max <= temp_range_max:
        plt.title(f"Max: {temp_max:.1f} {unit_temperature}            Avg: {temp_avg:.1f} {unit_temperature}            Min: {temp_min:.1f} {unit_temperature}", color=color_fg_set)
    elif temp_min < temp_range_min and temp_max <= temp_range_max:
        plt.title(f"Max: {temp_max:.1f} {unit_temperature}    Avg: {temp_avg:.1f} {unit_temperature}    *Min: {temp_range_min:.1f} {unit_temperature} ({temp_min:.1f} {unit_temperature})", color=color_fg_set)
    elif temp_min >= temp_range_min and temp_max > temp_range_max:
        plt.title(f"*Max: {temp_range_max:.1f} {unit_temperature} ({temp_max:.1f} {unit_temperature})    Avg: {temp_avg:.1f} {unit_temperature}    Min: {temp_min:.1f} {unit_temperature}", color=color_fg_set)
    elif temp_min < temp_range_min and temp_max > temp_range_max:
        plt.title(f"*Max: {temp_range_max:.1f} {unit_temperature} ({temp_max:.1f} {unit_temperature})    Avg: {temp_avg:.1f} {unit_temperature}    *Min: {temp_range_min:.1f} {unit_temperature} ({temp_min:.1f} {unit_temperature})", color=color_fg_set)

    plt.ylabel(dt.iso(unix), color = color_fg_set)  # Datetime

    plt.pause(0.001)  # required



# Change color theme
color_fg_set = COLOR_FG  # Store for refresh() plt.title color
def theme(fg = COLOR_FG, bg = COLOR_BG, cfg = config.get_dict()):
    global fig
    global color_fg_set
    color_fg_set = fg

    unit_temperature_cfg = cfg["unit_temperature"]

    if unit_temperature_cfg == "kelvin":
        unit_temperature = "K"
    elif unit_temperature_cfg == "celsius":
        unit_temperature = "°C"
    else:
        sys.exit("Error: UnknownTemperatureUnit")

    fig.patch.set_facecolor(bg)  # Background color

    cbar.ax.yaxis.set_tick_params(color=fg)  # Tick color
    cbar.set_label(f"Temperature [{unit_temperature}]", fontsize=14, color=fg)  # Label
    #cbar.set_label("Temperature [$^{\circ}$C]", fontsize=14, color=fg)  # Label
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=fg)  # Tick labels

#theme(COLOR_FG, COLOR_BG)
