import numpy as np
import config
import ui
import printf



#def test_pixels(frame_array, test_array):
#    pixels_results = []
#    test_array_rows = np.shape(test_array)[0]
#    for row in range(test_array_rows):
#        pixel_tested = _test_pixel(frame_array, test_array[row][0], test_array[row][1], test_array[row][2], test_array[row][3])
#        pixels_results.append(pixel_tested)
#
#    result = pixels_results.count(True), pixels_results.count(False)
#
#    return result

# Test pixels############################################################
# Tests if pixel is in tolerance and returns result. Called from measurement_points()
def _test_pixel(frame, row, column, temp_min, temp_max):
    if frame[row, column] >= temp_min and frame[row, column] <= temp_max:
        return True
    else:
        return False


def test_area(frame_array, test_array):
    pixels_results = []
    test_array_rows = np.shape(test_array)[0]
    for row in range(test_array_rows):
        y_list = range(int(test_array[row][0]), int(test_array[row][2] + 1))
        x_list = range(int(test_array[row][1]), int(test_array[row][3] + 1))

        for y in y_list:
            #print(y)
            for x in x_list:
                #print(x, y)
                pixel_tested = _test_pixel(frame_array, y, x, test_array[row][4], test_array[row][5])
                pixels_results.append(pixel_tested)

    result = pixels_results.count(True), pixels_results.count(False)

    return result


def _alarm(state, cfg = config.get_dict()):
    BUZZER = cfg["buzzer"]
    BUZZER_ALARM = cfg["monitor_buzzer"]

    if state:
        if BUZZER and BUZZER_ALARM:
            import buzzer
            buzzer.temp_alarm() # Acoustic notification for save.
        ui.theme(ui.COLOR_BG, ui.COLOR_TEMP_ALARM)
    else:
        ui.theme(ui.COLOR_FG, ui.COLOR_BG)


_printf_monitor_percent = -1
# Trigger alarm when temps not in tolerance
def temps(frame, test_list, cfg = config.get_dict()):
    global _printf_monitor_percent

    test_max_deviations = cfg["monitor_max_deviations"]
    test_invert = cfg["monitor_invert"]

    #result = test_pixels(frame, test_list)
    result = test_area(frame, test_list)
    result_percent = 100 / (result[0] + result[1]) * result[0]
    if test_invert:
        result_percent = 100 - result_percent

    # Print when percent changes
    if round(_printf_monitor_percent) != round(result_percent):
        printf.monitor_percent(result_percent)
        _printf_monitor_percent = result_percent

    if result_percent < 100 - test_max_deviations:
        _alarm(True)
    else:
        _alarm(False)
