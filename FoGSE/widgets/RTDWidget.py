"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.readers.RTDReader import RTDReader
from FoGSE.windows.RTDWindow import RTDWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget, QValueCheckWidget, QValueMultiRangeWidget, QValueListWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class RTDWidget(QWidget):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.RTDReader.RTDReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="RTD", image_angle=0, parent=None):

        QWidget.__init__(self, parent)
        rtd_parser = self.get_rtd_parsers()
        reader = rtd_parser(datafile=data_file)

        self._default_qvaluewidget_value = "<span>&#129418;</span>" #fox

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 700, 500
        self.setGeometry(100,100,self.detw, self.deth)
        # self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts for the status window, LED, buttons, times, and plot
        lc_layout = QtWidgets.QGridLayout()

        self.panels = dict() # for all the background panels

        rtd_window = self.get_rtd_windows()
        
        ## for Timepix light curve
        # widget for displaying the automated recommendation
        self._lc_layout = self.layout_bkg(main_layout=lc_layout, 
                                             panel_name="lc_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.lc = rtd_window(reader=reader, name=name)
        self.lc.setStyleSheet("border-width: 0px;")
        self._lc_layout.addWidget(self.lc)

        # self.lc.reader.value_changed_collection.connect(...)

        ## all widgets together
        # lc
        global_layout = QGridLayout()
        # global_layout.addWidget(self.lc, 0, 0, 4, 4)
        global_layout.addLayout(lc_layout, 0, 0, 6, 7)

        unifrom_layout_stretch(global_layout, grid=True)

        # lc_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._lc_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom


        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def get_rtd_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return RTDReader
    
    def get_rtd_windows(self):
        """ A way the class can be inherited from but use different parsers. """
        return RTDWindow

    def layout_bkg(self, main_layout, panel_name, style_sheet_string, grid=False):
        """ Adds a background widget (panel) to a main layout so border, colours, etc. can be controlled. """
        # create panel widget
        self.panels[panel_name] = QtWidgets.QWidget()

        # make the panel take up the main layout 
        main_layout.addWidget(self.panels[panel_name])

        # edit the main layout widget however you like
        self.panels[panel_name].setStyleSheet(style_sheet_string)

        # now return a new, child layout that inherits from the panel widget
        if grid:
            return QtWidgets.QGridLayout(self.panels[panel_name])
        else:
            return QtWidgets.QVBoxLayout(self.panels[panel_name])

    def _layout_style(self, border_colour, background_colour):
        """ Define a global layout style. """
        # return f"border-width: 2px; border-style: outset; border-radius: 10px; border-color: {border_colour}; background-color: {background_colour};"
        return f"border-width: 2px; border-style: outset; border-radius: 0px; border-color: {border_colour}; background-color: {background_colour};"
    
    def update_aspect(self, aspect_ratio):
        """ Update the lc aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        # lc_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.6))
        # self.lc.resize(lc_resize)
        # ped_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.4))
        # self.ped.resize(ped_resize)
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)


if __name__=="__main__":
    app = QApplication([])

    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run19/gse/housekeeping.log"
    
    # w.resize(1000,500)
    w = RTDWidget(data_file=DATAFILE)
    # w = QValueWidgetTest()
    w.show()
    app.exec()