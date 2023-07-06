## Reads RAW file and displays it.
import os.path
import sys

import config
import frametools
import ui




def read(cfg):
    ui.init(cfg)

    # Get frame
    frame_raw = cfg["frame"]
    utime = cfg["timestamp"]
    # Apply emissivity adjustment
    frame_adjusted = frametools.adjust_emissivity(frame_raw, cfg = cfg)
    # Display frame
    for i in range(2): # Frame needs to be refreshed twice for the colorbar to adjust to min and max temp. (dunno why ¯\_(°_°)_/¯ ?!)
        ui.refresh(frame_adjusted, utime, cfg = cfg)

    if len(sys.argv) > 3:
        if sys.argv[2] == "--save":
            import dt
            dirname = os.path.dirname(sys.argv[1])
            save_format = sys.argv[3]

            save_path = os.path.join(dirname, cfg["save_prefix"] + dt.simple(int(cfg["timestamp"])) + cfg["save_suffix"] + "." + save_format)
            ui.plt.savefig(save_path, format=save_format)
            sys.exit()

    ui.plt.show(block=True)

if __name__ == "__main__":
    cfg = config.get_dict()
    read(cfg)