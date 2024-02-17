"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

# from FoGSE.read_raw_to_refined.readRawToRefinedPower import PowerReader
# from FoGSE.windows.PowerWindow import PowerWindow
from FoGSE.widgets.QValueWidget import QValueWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class PowerWidget(QWidget):
    """
    An individual window to display Power data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedPower.PowerReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="Power", image_angle=0, parent=None):

        QWidget.__init__(self, parent)
        # self.reader_power = PowerReader(datafile=data_file)

        self._default_qvaluewidget_value = "<span>&#129418;</span>" #fox

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 950, 300
        self.setGeometry(100,100,self.detw, self.deth)
        # self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        self.panels = dict() # for all the background panels

        # need to groupd some of these for the layout
        first_layout = QtWidgets.QGridLayout()
        first_layout_colour = "rgb(53, 108, 117)"
        self._first_layout = self.layout_bkg(main_layout=first_layout, 
                                             panel_name="first_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)

        self.p0 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p1 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p2 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p3 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p4 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p5 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p6 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p7 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p8 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p9 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p10 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p11 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p12 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p13 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p14 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        self.p15 = QValueWidget(name="Board T1", value=self._default_qvaluewidget_value, border_colour=first_layout_colour)
        
        self._first_layout.addWidget(self.p0, 0, 0, 1, 2) 
        self._first_layout.addWidget(self.p1, 0, 2, 1, 2) 
        self._first_layout.addWidget(self.p2, 0, 4, 1, 2) 
        self._first_layout.addWidget(self.p3, 0, 6, 1, 2) 
        self._first_layout.addWidget(self.p4, 1, 0, 1, 2) 
        self._first_layout.addWidget(self.p5, 1, 2, 1, 2) 
        self._first_layout.addWidget(self.p6, 1, 4, 1, 2) 
        self._first_layout.addWidget(self.p7, 1, 6, 1, 2) 
        self._first_layout.addWidget(self.p8, 2, 0, 1, 2) 
        self._first_layout.addWidget(self.p9, 2, 2, 1, 2) 
        self._first_layout.addWidget(self.p10, 2, 4, 1, 2) 
        self._first_layout.addWidget(self.p11, 2, 6, 1, 2) 
        self._first_layout.addWidget(self.p12, 3, 0, 1, 2) 
        self._first_layout.addWidget(self.p13, 3, 2, 1, 2) 
        self._first_layout.addWidget(self.p14, 3, 4, 1, 2) 
        self._first_layout.addWidget(self.p15, 3, 6, 1, 2) 

        unifrom_layout_stretch(self._first_layout, grid=True)
        unifrom_layout_stretch(first_layout, grid=True)
        
        set_all_spacings(self._first_layout)
        set_all_spacings(first_layout)
        # set_all_spacings(self._second_layout)

        # self.reader_power.value_changed_collection.connect(self.all_fields)

        ## all widgets together
        # lc
        global_layout = QGridLayout()
        set_all_spacings(global_layout)

        global_layout.addLayout(first_layout, 0, 0, 6, 8)#,
        # global_layout.addLayout(second_layout, 6, 0, 1, 9)#,

        unifrom_layout_stretch(global_layout, grid=True)
        # unifrom_layout_stretch(self._second_layout, grid=True)

        self._first_layout.setContentsMargins(0, 0, 0, 0)
        # self._second_layout.setContentsMargins(0, 0, 0, 0)
        # self._second_layout.setSpacing(6)

        # asic_layout.setSpacing(0)
        first_layout.setSpacing(0)
        # second_layout.setSpacing(0)
        # ping_layout.setSpacing(0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def all_fields(self):
        """ Update the QValueWidgets. """
        
        self.p0.update_label(self.reader_power.collection.something())
        self.p1.update_label(self.reader_power.collection.something())
        self.p2.update_label(self.reader_power.collection.something())
        self.p3.update_label(self.reader_power.collection.something())
        self.p4.update_label(self.reader_power.collection.something())
        self.p5.update_label(self.reader_power.collection.something())
        self.p6.update_label(self.reader_power.collection.something())
        self.p7.update_label(self.reader_power.collection.something())
        self.p8.update_label(self.reader_power.collection.something())
        self.p9.update_label(self.reader_power.collection.something())
        self.p10.update_label(self.reader_power.collection.something())
        self.p11.update_label(self.reader_power.collection.something())
        self.p12.update_label(self.reader_power.collection.something())
        self.p13.update_label(self.reader_power.collection.something())
        self.p14.update_label(self.reader_power.collection.something())
        self.p15.update_label(self.reader_power.collection.something())


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

    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"
    
    # w.resize(1000,500)
    # w = AllCdTeView(cdte0, cdte1, cdte2, cdte3)
    w = PowerWidget(data_file=datafile)
    # w = QValueWidgetTest()
    w.show()
    app.exec()