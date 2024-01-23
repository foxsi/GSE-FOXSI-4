"""
A demo to walk through an existing CdTe raw file.
"""
import datetime
import os
import re

import numpy as np
from PyQt6.QtWidgets import QApplication

from demo_foxsi_dets import run_windows

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

def newest_data():
    """ Return the directory of the newest folder containg data. """
    _log_files = FILE_DIR+"/../../../logs/received/"

    _folders = [re.findall("\d+\-\d+\-\d+\_\d+\:\d+\:\d+", f) for f in os.listdir(_log_files)]
    _time_folders = [tf[0] for tf in _folders if len(tf)==1]
    
    dts = [datetime.strptime(ts, "%d/%m/%y %H:%M:%S") for ts in _time_folders]

    return _log_files+_time_folders[np.argmax(dts)]

if __name__=="__main__":
    app = QApplication([])

    newest_folder = newest_data()

    instruments = [inst for inst in os.listdir(newest_folder) if (inst.startswith("cdte") or inst.startswith("cmos"))]

    windows_and_files = []
    for inst in instruments:
        if inst.startswith("cdte"):
            windows_and_files.append(f"cdte_ped {newest_folder}/{inst}")
            windows_and_files.append(f"cdte_im {newest_folder}/{inst}")
        elif inst.startswith("cmos"):
            windows_and_files.append(f"cdte_pc {newest_folder}/{inst}")
            windows_and_files.append(f"cdte_ql {newest_folder}/{inst}")

    run_windows(*windows_and_files)