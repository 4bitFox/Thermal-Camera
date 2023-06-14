import numpy as np
import config
import ui


BUZZER = config.BUZZER
BUZZER_ALARM = config.TEST_BUZZER

test_max_deviations = config.TEST_MAX_DEVIATIONS
test_invert = config.TEST_INVERT


# Check pixels if in tolerance. Returns True if ALL pixels are in tolerance.
def test_pixels(frame_array, test_array):
    pixels_results = []
    test_array_rows = np.shape(test_array)[0]
    for row in range(test_array_rows):
        pixel_tested = _test(frame_array, test_array[row][0], test_array[row][1], test_array[row][2], test_array[row][3])
        pixels_results.append(pixel_tested)

    result = pixels_results.count(True), pixels_results.count(False)

    return result



# Test pixels############################################################
# Tests if pixel is in tolerance and returns result. Called from measurement_points()
def _test(pixel, row, column, temp_min, temp_max):
    if pixel[row, column] > temp_min and pixel[row, column] < temp_max:
        return True
    else:
        return False



def _alarm(state):
    if state:
        if BUZZER and BUZZER_ALARM:
            import buzzer
            buzzer.temp_alarm() # Acoustic notification for save.
        ui.theme(ui.COLOR_BG, ui.COLOR_TEMP_ALARM)
    else:
        ui.theme(ui.COLOR_FG, ui.COLOR_BG)


# Trigger alarm when temps not in tolerance
def temps(frame, test_list):
    result = test_pixels(frame, test_list)
    print(result)
    if not test_invert:
        if result[1] > test_max_deviations:
            _alarm(True)
        else:
            _alarm(False)
    else:
        if result[1] <= test_max_deviations:
            _alarm(True)
        else:
            _alarm(False)