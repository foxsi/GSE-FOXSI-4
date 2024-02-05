"""
A module for general IO, file, directory handling etc.
"""
import datetime
import os
import re

import numpy as np

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

def newest_data_dir():
    """ Return the directory of the newest folder containg data. """
    _log_files = FILE_DIR+"/../../logs/received/"

    _folders = [re.findall("\d+\-\d+\-\d+\_\d+\-\d+\-\d+", f) for f in os.listdir(_log_files)]
    _time_folders = [tf[0] for tf in _folders if len(tf)==1]
    
    dts = [datetime.datetime.strptime(ts, "%d-%m-%Y_%H-%M-%S") for ts in _time_folders]

    return _log_files+_time_folders[np.argmax(dts)]