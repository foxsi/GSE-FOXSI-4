"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.read_raw_to_refined.readRawToRefinedTimepix import TimepixReader
from FoGSE.windows.TimepixWindow import TimepixWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget, QValueWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class TimepixWidget(QWidget):
    """
    An individual window to display Timepi data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedTimepi. TimepixReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="Timepix", image_angle=0, parent=None):

        QWidget.__init__(self, parent)
        reader = TimepixReader(datafile=data_file)

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 600, 400
        self.setGeometry(100,100,self.detw, self.deth)
        # self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts for the status window, LED, buttons, times, and plot
        lc_layout = QtWidgets.QGridLayout()

        self.panels = dict() # for all the background panels
        
        ## for Timepix light curve
        # widget for displaying the automated recommendation
        self._lc_layout = self.layout_bkg(main_layout=lc_layout, 
                                             panel_name="lc_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.lc = TimepixWindow(reader=reader, name=name)
        self.lc.setStyleSheet("border-width: 0px;")
        self._lc_layout.addWidget(self.lc)

        # need to groupd some of these for the layout
        first_layout = QtWidgets.QGridLayout()
        first_layout_colour = "rgb(53, 108, 117)"
        self._first_layout = self.layout_bkg(main_layout=first_layout, 
                                             panel_name="first_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.mtot = QValueRangeWidget(name="Meant ToT", value="N/A", condition={"low":0,"high":np.inf}, border_colour=first_layout_colour)
        self.flx = QValueRangeWidget(name="Flux", value="N/A", condition={"low":0,"high":np.inf}, border_colour=first_layout_colour)
        self.flgs = QValueRangeWidget(name="Flags", value=60, condition={"low":2,"high":15}, border_colour=first_layout_colour)
        self.someting1 = QValueRangeWidget(name="someting1", value=60, condition={"low":2,"high":15}, border_colour=first_layout_colour)
        self.someting2 = QValueRangeWidget(name="someting2", value=60, condition={"low":2,"high":15}, border_colour=first_layout_colour)
        self.someting5 = QValueRangeWidget(name="someting5", value=60, condition={"low":2,"high":15}, border_colour=first_layout_colour)
        self.someting6 = QValueRangeWidget(name="someting6", value=60, condition={"low":2,"high":15}, border_colour=first_layout_colour)
        self._first_layout.addWidget(self.mtot, 0, 0, 1, 2) 
        self._first_layout.addWidget(self.flx, 1, 0, 1, 2) 
        self._first_layout.addWidget(self.flgs, 2, 0, 1, 2) 
        self._first_layout.addWidget(self.someting1, 3, 0, 1, 2) 
        self._first_layout.addWidget(self.someting2, 4, 0, 1, 2) 
        self._first_layout.addWidget(self.someting5, 5, 0, 1, 2) 
        self._first_layout.addWidget(self.someting6, 6, 0, 1, 2) 
        # next
        second_layout = QtWidgets.QGridLayout()
        second_layout_colour = "rgb(213, 105, 48)"
        self._second_layout = self.layout_bkg(main_layout=second_layout, 
                                              panel_name="second_panel", 
                                              style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.cts = QValueRangeWidget(name="Ct", value="N/A", condition={"low":0,"high":np.inf}, border_colour=second_layout_colour)
        self.ctr = QValueRangeWidget(name="Ct/s", value=14, condition={"low":2,"high":15}, border_colour=second_layout_colour)
        self.someting3 = QValueRangeWidget(name="someting3", value=14, condition={"low":2,"high":15}, border_colour=second_layout_colour)
        self.someting4 = QValueRangeWidget(name="someting4", value=14, condition={"low":2,"high":15}, border_colour=second_layout_colour)
        self._second_layout.addWidget(self.cts, 0, 0, 1, 2) 
        self._second_layout.addWidget(self.ctr, 0, 2, 1, 2) 
        self._second_layout.addWidget(self.someting3, 0, 4, 1, 2) 
        self._second_layout.addWidget(self.someting4, 0, 6, 1, 2) 
        
        set_all_spacings(self._first_layout)
        set_all_spacings(self._second_layout)

        self.lc.reader.value_changed_collection.connect(self.all_fields)

        ## all widgets together
        # lc
        global_layout = QGridLayout()
        # global_layout.addWidget(self.lc, 0, 0, 4, 4)
        global_layout.addLayout(lc_layout, 0, 0, 6, 7)

        global_layout.addLayout(first_layout, 0, 7, 6, 2)#,
        global_layout.addLayout(second_layout, 6, 0, 1, 9)#,

        unifrom_layout_stretch(global_layout, grid=True)
        unifrom_layout_stretch(self._first_layout, grid=True)
        unifrom_layout_stretch(self._second_layout, grid=True)

        # lc_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._lc_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._first_layout.setContentsMargins(0, 0, 0, 0)
        self._second_layout.setContentsMargins(0, 0, 0, 0)
        # self._second_layout.setSpacing(6)

        # asic_layout.setSpacing(0)
        first_layout.setSpacing(0)
        second_layout.setSpacing(0)
        # ping_layout.setSpacing(0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def all_fields(self):
        """ 
        Update the:
        * count rate field, 
        """
        self.mtot.update_label(self.lc.reader.collection.get_mean_tot())
        self.flx.update_label(self.lc.reader.collection.get_flux())
        self.flgs.update_label(self.lc.reader.collection.get_flags())

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

class AllCdTeView(QWidget):
    def __init__(self, cdte0, cdte1, cdte2, cdte3):
        super().__init__()     
        
        # self.setGeometry(100,100,2000,350)
        self.detw, self.deth = 2000,500
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(600,150)
        self.setWindowTitle("All CdTe View")
        self.aspect_ratio = self.detw/self.deth

        # datafile0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeTrialsOfParser-20231102/cdte.log"
        # datafile1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte2.log"
        # datafile2 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte3.log"
        # datafile3 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte4.log"

        f0 = CdTeWidget(data_file=cdte0, name=os.path.basename(cdte0), image_angle=-120)
        # f0.resize(QtCore.QSize(150, 190))
        _f0 =QHBoxLayout()
        _f0.addWidget(f0)

        f1 = CdTeWidget(data_file=cdte1, name=os.path.basename(cdte1), image_angle=-30)
        # f1.resize(QtCore.QSize(150, 150))
        _f1 =QGridLayout()
        _f1.addWidget(f1, 0, 0)

        f2 = CdTeWidget(data_file=cdte2, name=os.path.basename(cdte2), image_angle=-90)
        # f2.resize(QtCore.QSize(150, 150))
        _f2 =QGridLayout()
        _f2.addWidget(f2, 0, 0)

        f3 = CdTeWidget(data_file=cdte3, name=os.path.basename(cdte3), image_angle=+30)
        # f3.resize(QtCore.QSize(150, 150))
        _f3 =QGridLayout()
        _f3.addWidget(f3, 0, 0)

        lay = QGridLayout(spacing=0)
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

        # lay.addWidget(f0, 0, 0, 1, 1)
        # lay.addWidget(f1, 0, 1, 1, 1)
        lay.addLayout(_f0, 0, 0, 1, 1)
        lay.addLayout(_f1, 0, 1, 1, 1)
        lay.addLayout(_f2, 0, 2, 1, 1)
        lay.addLayout(_f3, 0, 3, 1, 1)

        lay.setContentsMargins(2, 2, 2, 2) # left, top, right, bottom
        lay.setHorizontalSpacing(5)
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        self.setLayout(lay)

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        # image_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.6))
        # self.image.resize(image_resize)
        # ped_resize = QtCore.QSize(int(event.size().width()*0.6), int(event.size().height()*0.4))
        # self.ped.resize(ped_resize)
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)

if __name__=="__main__":
    app = QApplication([])

    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    
    # w.resize(1000,500)
    # w = AllCdTeView(cdte0, cdte1, cdte2, cdte3)
    w = TimepixWidget(data_file=datafile)
    
    w.show()
    app.exec()