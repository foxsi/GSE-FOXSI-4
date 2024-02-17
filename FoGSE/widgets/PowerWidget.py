"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.read_raw_to_refined.readRawToRefinedPower import PowerReader
# from FoGSE.windows.PowerWindow import PowerWindow
from FoGSE.widgets.QValueWidget import QValueWidget, QValueMultiRangeWidget
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
        self.reader_power = PowerReader(datafile=data_file)

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
        
        _off = [-0.05, 0.05, "white"]
        p0_cond = {"range1":_off, "range2":[24,32,"green"], "other":"orange", "error":"orange"}
        p1_cond = {"range1":_off, "range2":[5.5,6,"green"], "other":"orange", "error":"orange"}
        p2_cond = {"range1":_off, "range2":[12,13,"green"], "other":"orange", "error":"orange"}
        p3_cond = {"range1":_off, "range2":[5,5.5,"green"], "other":"orange", "error":"orange"}
        p4_cond = {"range1":_off, "range2":[0.1,3,"green"], "other":"orange", "error":"orange"}
        p5_cond = {"range1":_off, "range2":[0,20,"green"], "other":"orange", "error":"orange"}
        p6_cond = {"range1":_off, "range2":[0,20,"green"], "other":"orange", "error":"orange"}
        p7_cond = {"range1":_off, "range2":[0,20,"green"], "other":"orange", "error":"orange"}
        p8_cond = {"range1":_off, "range2":[0,20,"green"], "other":"orange", "error":"orange"}
        p9_cond = {"range1":_off, "range2":[0.2,0.4,"green"], "other":"orange", "error":"orange"}
        p10_cond = {"range1":_off, "range2":[0.1,0.2,"green"], "other":"orange", "error":"orange"}
        p11_cond = {"range1":_off, "range2":[0.1,0.2,"green"], "other":"orange", "error":"orange"}
        p12_cond = {"range1":_off, "range2":[0.1,0.2,"green"], "other":"orange", "error":"orange"}
        p13_cond = {"range1":_off, "range2":[0.1,0.2,"green"], "other":"orange", "error":"orange"}
        p14_cond = {"range1":_off, "range2":[0.2,0.4,"green"], "other":"orange", "error":"orange"}
        p15_cond = {"range1":_off, "range2":[0.2,0.4,"green"], "other":"orange", "error":"orange"}

        self.p0 = QValueMultiRangeWidget(name="28 V", value=self._default_qvaluewidget_value, condition=p0_cond, border_colour=first_layout_colour)
        self.p1 = QValueMultiRangeWidget(name="5.5 V", value=self._default_qvaluewidget_value, condition=p1_cond, border_colour=first_layout_colour)
        self.p2 = QValueMultiRangeWidget(name="12 V", value=self._default_qvaluewidget_value, condition=p2_cond, border_colour=first_layout_colour)
        self.p3 = QValueMultiRangeWidget(name="5 V", value=self._default_qvaluewidget_value, condition=p3_cond, border_colour=first_layout_colour)
        self.p4 = QValueMultiRangeWidget(name="Reg. [A]", value=self._default_qvaluewidget_value, condition=p4_cond, border_colour=first_layout_colour)
        self.p5 = QValueMultiRangeWidget(name="SAAS 12 V [A]", value=self._default_qvaluewidget_value, condition=p5_cond, border_colour=first_layout_colour)
        self.p6 = QValueMultiRangeWidget(name="SAAS 5 V [A]", value=self._default_qvaluewidget_value, condition=p6_cond, border_colour=first_layout_colour)
        self.p7 = QValueMultiRangeWidget(name="TimP 12 V [A]", value=self._default_qvaluewidget_value, condition=p7_cond, border_colour=first_layout_colour)
        self.p8 = QValueMultiRangeWidget(name="TimP 5 V [A]", value=self._default_qvaluewidget_value, condition=p8_cond, border_colour=first_layout_colour)
        self.p9 = QValueMultiRangeWidget(name="DE [A]", value=self._default_qvaluewidget_value, condition=p9_cond, border_colour=first_layout_colour)
        self.p10 = QValueMultiRangeWidget(name="CdTe1 [A]", value=self._default_qvaluewidget_value, condition=p10_cond, border_colour=first_layout_colour)
        self.p11 = QValueMultiRangeWidget(name="CdTe2 [A]", value=self._default_qvaluewidget_value, condition=p11_cond, border_colour=first_layout_colour)
        self.p12 = QValueMultiRangeWidget(name="CdTe3 [A]", value=self._default_qvaluewidget_value, condition=p12_cond, border_colour=first_layout_colour)
        self.p13 = QValueMultiRangeWidget(name="CdTe4 [A]", value=self._default_qvaluewidget_value, condition=p13_cond, border_colour=first_layout_colour)
        self.p14 = QValueMultiRangeWidget(name="CMOS1 [A]", value=self._default_qvaluewidget_value, condition=p14_cond, border_colour=first_layout_colour)
        self.p15 = QValueMultiRangeWidget(name="CMOS2 [A]", value=self._default_qvaluewidget_value, condition=p15_cond, border_colour=first_layout_colour)

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

        self.reader_power.value_changed_collection.connect(self.all_fields)

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
        
        self.p0.update_label(round(self.reader_power.collection.get_p0(),3))
        self.p1.update_label(round(self.reader_power.collection.get_p1(),3))
        self.p2.update_label(round(self.reader_power.collection.get_p2(),3))
        self.p3.update_label(round(self.reader_power.collection.get_p3(),3))
        self.p4.update_label(round(self.reader_power.collection.get_p4(),3))
        self.p5.update_label(round(self.reader_power.collection.get_p5(),3))
        self.p6.update_label(round(self.reader_power.collection.get_p6(),3))
        self.p7.update_label(round(self.reader_power.collection.get_p7(),3))
        self.p8.update_label(round(self.reader_power.collection.get_p8(),3))
        self.p9.update_label(round(self.reader_power.collection.get_p9(),3))
        self.p10.update_label(round(self.reader_power.collection.get_p10(),3))
        self.p11.update_label(round(self.reader_power.collection.get_p11(),3))
        self.p12.update_label(round(self.reader_power.collection.get_p12(),3))
        self.p13.update_label(round(self.reader_power.collection.get_p13(),3))
        self.p14.update_label(round(self.reader_power.collection.get_p14(),3))
        self.p15.update_label(round(self.reader_power.collection.get_p15(),3))


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