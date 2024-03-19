"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings
from FoGSE.widgets.DisplayCommandWidget import DisplayCommandWidget


class DisplayCommandPlaybackWidget(DisplayCommandWidget):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.RTDReader.RTDReader()`.
        Default: None
    """
    def __init__(self, name="DisplayCommand", parent=None):

        DisplayCommandWidget.__init__(self, name, parent)


if __name__=="__main__":
    app = QApplication([])
    
    # w.resize(1000,500)
    w = DisplayCommandPlaybackWidget()
    # w = QValueWidgetTest()
    w.show()
    app.exec()