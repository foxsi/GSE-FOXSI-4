"""
A widget to show off CMOS data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.read_raw_to_refined.readRawToRefinedCMOSPC import CMOSPCReader
from FoGSE.read_raw_to_refined.readRawToRefinedCMOSQL import CMOSQLReader
from FoGSE.windows.CMOSPCWindow import CMOSPCWindow
from FoGSE.windows.CMOSQLWindow import CMOSQLWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch


class CMOSWidget(QWidget):
    """
    An individual window to display CMOS data read from a file.

    Parameters
    ----------
    data_file_pc, data_file_ql : `str`, `str`
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedCMOSPC.CMOSPCReader()` 
        and `FoGSE.read_raw_to_refined.readRawToRefinedCMOSQL.CMOSQLReader()`,
        respectively.
        Default: None

    plotting_product : `str`
        String to determine whether an "image" and or "spectrogram" should be shown.
        Default: "image"
    """
    def __init__(self, data_file_pc=None, data_file_ql=None, name="CMOS", parent=None):

        QWidget.__init__(self, parent)
        reader_pc = CMOSPCReader(datafile=data_file_pc)
        reader_ql = CMOSQLReader(datafile=data_file_ql)

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 100, 50
        # self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts for the status window, LED, buttons, times, and plot
        ql_layout = QtWidgets.QGridLayout()
        pc_layout = QtWidgets.QGridLayout()
        value_layout = QtWidgets.QVBoxLayout()
        # image_layout.setColumnStretch(0,1)
        # image_layout.setRowStretch(0,1)

        self.panels = dict() # for all the background panels
        
        ## for CdTe image
        # widget for displaying the automated recommendation
        self._ql_layout = self.layout_bkg(main_layout=ql_layout, 
                                             panel_name="ql_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"), grid=True)
        self.ql = CMOSQLWindow(reader=reader_ql, plotting_product="image", name=name)
        # self.image.setMinimumSize(QtCore.QSize(400,400)) # was 250,250
        # self.image.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.ql.setStyleSheet("border-width: 0px;")
        self._ql_layout.addWidget(self.ql)
        
        # image_layout.addWidget(self.image)
        # self._image_layout.setColumnStretch(0, 1)
        # self._image_layout.setRowStretch(0, 1)

        ## for CdTe pedestal
        # widget for displaying the automated recommendation
        self._pc_layout = self.layout_bkg(main_layout=pc_layout, 
                                             panel_name="pc_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"), grid=True)
        self.pc = CMOSPCWindow(reader=reader_pc, plotting_product="image", name=name)
        # self.ped.setMinimumSize(QtCore.QSize(400,200)) # was 250,250
        # self.ped.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.pc.setStyleSheet("border-width: 0px;")
        self._pc_layout.addWidget(self.pc) 
        # self._ped_layout.setColumnStretch(0, 1)
        # self._ped_layout.setRowStretch(0, 1)

        # status values
        self._value_layout = self.layout_bkg(main_layout=value_layout, 
                                             panel_name="value_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"))
        self.cts = QValueRangeWidget(name="Counts (cts)", value="N/A", condition={"low":0,"high":np.inf})
        self.somevalue0 = QValueRangeWidget(name="This", value=9, condition={"low":2,"high":15})
        self.somevalue1 = QValueRangeWidget(name="That", value=8, condition={"low":2,"high":15})
        self.somevalue2 = QValueRangeWidget(name="Other", value=60, condition={"low":2,"high":15})
        self.somevalue3 = QValueRangeWidget(name="Another", value="N/A", condition={"low":2,"high":15})
        self.somevalue4 = QValueRangeWidget(name="Again", value=2, condition={"low":2,"high":15})
        self.somevalue5 = QValueRangeWidget(name="This2", value=14, condition={"low":2,"high":15})
        self._value_layout.addWidget(self.cts) 
        self._value_layout.addWidget(self.somevalue0) 
        self._value_layout.addWidget(self.somevalue1) 
        self._value_layout.addWidget(self.somevalue2) 
        self._value_layout.addWidget(self.somevalue3) 
        self._value_layout.addWidget(self.somevalue4) 
        self._value_layout.addWidget(self.somevalue5) 
        # self.somevalue0.setMinimumSize(QtCore.QSize(200,100))
        # self.somevalue1.setMinimumSize(QtCore.QSize(200,100))
        # self.somevalue2.setMinimumSize(QtCore.QSize(200,100))
        # self.somevalue3.setMinimumSize(QtCore.QSize(200,100))
        # self.somevalue4.setMinimumSize(QtCore.QSize(200,100))
        # self.somevalue5.setMinimumSize(QtCore.QSize(200,100))

        temp_layout = QtWidgets.QVBoxLayout()
        self._temp_layout = self.layout_bkg(main_layout=temp_layout, 
                                             panel_name="temp_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"))
        self.fpga_temp = QValueRangeWidget(name="FPGA T", value="N/A", condition={"low":0,"high":np.inf})
        self.sensor_temp = QValueRangeWidget(name="Sensor T", value="N/A", condition={"low":0,"high":np.inf})
        self._temp_layout.addWidget(self.fpga_temp) 
        self._temp_layout.addWidget(self.sensor_temp) 
        self.set_all_spacings(self._temp_layout)

        phot_layout = QtWidgets.QVBoxLayout()
        self._phot_layout = self.layout_bkg(main_layout=phot_layout, 
                                             panel_name="phot_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"))
        self.ph_w = QValueRangeWidget(name="Whole Ph. R.", value="N/A", condition={"low":0,"high":np.inf})
        self.ph_p = QValueRangeWidget(name="Part Ph. R.", value="N/A", condition={"low":0,"high":np.inf})
        self._phot_layout.addWidget(self.ph_w) 
        self._phot_layout.addWidget(self.ph_p) 
        self.set_all_spacings(self._phot_layout)

        comp_layout = QtWidgets.QVBoxLayout()
        self._comp_layout = self.layout_bkg(main_layout=comp_layout, 
                                             panel_name="comp_panel", 
                                             style_sheet_string=self._layout_style("grey", "white"))
        self.cpu = QValueRangeWidget(name="CPU Load Ave.", value="N/A", condition={"low":0,"high":np.inf})
        self.mem = QValueRangeWidget(name="R. Disk Size", value="N/A", condition={"low":0,"high":np.inf})
        self._comp_layout.addWidget(self.cpu) 
        self._comp_layout.addWidget(self.mem)

        # self.ql.reader.value_changed_collection.connect(self.all_fields)
        # -- or --
        # self.pc.reader.value_changed_collection.connect(self.all_fields)

        ## all widgets together
        # image
        global_layout = QGridLayout()
        # global_layout.addWidget(self.image, 0, 0, 4, 4)
        global_layout.addLayout(ql_layout, 0, 0, 40, 43)#,
                                #alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop) # y,x,h,w
        # pedestal
        # global_layout.addWidget(self.ped, 4, 0, 4, 3)
        global_layout.addLayout(pc_layout, 0, 43, 18, 36)#,
                                #alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)# y,x,h,w
        # status values
        # global_layout.addWidget(self.somevalue0, 0, 4, 1, 1)
        # global_layout.addWidget(self.somevalue1, 1, 4, 1, 1)
        # global_layout.addWidget(self.somevalue2, 2, 4, 1, 1)
        # global_layout.addWidget(self.somevalue3, 3, 4, 1, 1)
        # global_layout.addWidget(self.somevalue4, 4, 4, 1, 1)
        # global_layout.addWidget(self.somevalue5, 5, 4, 1, 1)
        # global_layout.addWidget(self.somevalue5, 6, 4, 1, 1)
        
        global_layout.addLayout(temp_layout, 40, 0, 10, 22)
        global_layout.addLayout(phot_layout, 40, 22, 10, 21)
        # global_layout.addLayout(comp_layout, 40, 29, 10, 14)
        global_layout.addLayout(value_layout, 18, 43, 32, 57)#,
                                #alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom)
        
        # make sure all cell sizes in the grid expand in proportion
        # for col in range(global_layout.columnCount()):
        #     global_layout.setColumnStretch(col, 1)
        # for row in range(global_layout.rowCount()):
        #     global_layout.setRowStretch(row, 1)
        unifrom_layout_stretch(global_layout)

        # image_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._ql_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        # ped_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._pc_layout.setContentsMargins(0, 0, 0, 0)
        self._value_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def set_all_spacings(self, layout, s=0, grid=False):
        """ Default is to remove all margins"""
        if grid:
            layout.setHorizontalSpacing(s)
            layout.setVerticalSpacing(s)
        else:
            layout.setSpacing(s)
        layout.setContentsMargins(s, s, s, s)

    def all_fields(self):
        """ 
        Update the:
        * count rate field, 
        """
        self.cts.update_label(self.ql.reader.collection.total_counts())

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
        """ Update the image aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

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

class AllCMOSView(QWidget):
    def __init__(self):
        super().__init__()     
        
        # self.setGeometry(100,100,2000,350)
        self.detw, self.deth = 2000,498
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(600,150)
        self.setWindowTitle("All CdTe View")
        self.aspect_ratio = self.detw/self.deth

        data_file_pc = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
        data_file_ql = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL

        f0 = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql, name=os.path.basename(data_file_pc))
        # f0.resize(QtCore.QSize(150, 190))
        _f0 =QHBoxLayout()
        _f0.addWidget(f0)

        f1 = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql, name=os.path.basename(data_file_pc))
        # f1.resize(QtCore.QSize(150, 150))
        _f1 =QGridLayout()
        _f1.addWidget(f1, 0, 0)

        lay = QGridLayout(spacing=0)
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

        # lay.addWidget(f0, 0, 0, 1, 1)
        # lay.addWidget(f1, 0, 1, 1, 1)
        lay.addLayout(_f0, 0, 0, 1, 1)
        lay.addLayout(_f1, 0, 1, 1, 1)

        unifrom_layout_stretch(lay)

        lay.setContentsMargins(1, 1, 1, 1) # left, top, right, bottom
        lay.setHorizontalSpacing(0)
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(83, 223, 221, 50);")

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
    
    data_file_pc = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
    data_file_ql = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL
    
    # w.resize(1000,500)
    w = AllCMOSView()
    # w = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql)
    
    w.show()
    app.exec()