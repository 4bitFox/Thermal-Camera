## Reads RAW file and displays it.

import config
import frametools
import ui


# Get frame
frame_raw = config.FRAME
utime = config.TIMESTAMP
# Apply emissivity adjustment
frame_adjusted = frametools.adjust_emissivity(frame_raw)
# Display frame
for i in range(2): # Frame needs to be refreshed twice for the colorbar to adjust to min and max temp. (dunno why ¯\_(°_°)_/¯ ?!)
    ui.refresh(frame_adjusted, utime)
ui.plt.show(block=True)
