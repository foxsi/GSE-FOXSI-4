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
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


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
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts 
        ql_layout = QtWidgets.QGridLayout()
        pc_layout = QtWidgets.QGridLayout()
        exp_layout = QtWidgets.QGridLayout()
        operation_layout = QtWidgets.QGridLayout()
        # image_layout.setColumnStretch(0,1)
        # image_layout.setRowStretch(0,1)

        self.panels = dict() # for all the background panels
        
        ## for CdTe image
        # widget for displaying the automated recommendation
        self._ql_layout = self.layout_bkg(main_layout=ql_layout, 
                                             panel_name="ql_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.ql = CMOSQLWindow(reader=reader_ql, plotting_product="image", name=name, integrate=True)
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
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.pc = CMOSPCWindow(reader=reader_pc, plotting_product="image", name=name, integrate=True)
        # self.ped.setMinimumSize(QtCore.QSize(400,200)) # was 250,250
        # self.ped.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.pc.setStyleSheet("border-width: 0px;")
        self._pc_layout.addWidget(self.pc) 
        # self._ped_layout.setColumnStretch(0, 1)
        set_all_spacings(pc_layout, grid=True)
        # self._ped_layout.setRowStretch(0, 1)

        # exposure values
        exp_layout_colour = "rgb(227, 116, 51)"
        self._exp_layout = self.layout_bkg(main_layout=exp_layout, 
                                             panel_name="exp_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), 
                                             grid=True)
        self.gain_m = QValueRangeWidget(name="Gain Mode", value=10, condition={"low":0,"high":np.inf}, border_colour=exp_layout_colour)
        self.exp_ql = QValueRangeWidget(name="QL Exp.", value=9, condition={"low":2,"high":np.inf}, border_colour=exp_layout_colour)
        self.exp_pc = QValueRangeWidget(name="PC Exp.", value=8, condition={"low":2,"high":np.inf}, border_colour=exp_layout_colour)
        self.rn = QValueRangeWidget(name="Repeat \"n\"", value=12, condition={"low":2,"high":15}, border_colour=exp_layout_colour)
        self.rN = QValueRangeWidget(name="Repeat \"N\"", value=14, condition={"low":2,"high":15}, border_colour=exp_layout_colour)
        self.gain_e = QValueRangeWidget(name="Gain Even", value=2, condition={"low":2,"high":15}, border_colour=exp_layout_colour)
        self.gain_o = QValueRangeWidget(name="Gain Odd", value=2, condition={"low":2,"high":15}, border_colour=exp_layout_colour)
        self.ncapture = QValueRangeWidget(name="NCapture", value=2, condition={"low":2,"high":15}, border_colour=exp_layout_colour)
        self._exp_layout.addWidget(self.gain_m, 0, 0, 1, 2) 
        self._exp_layout.addWidget(self.exp_ql, 2, 1, 1, 2) 
        self._exp_layout.addWidget(self.exp_pc, 2, 3, 1, 2) 
        self._exp_layout.addWidget(self.rn, 1, 0, 1, 2) 
        self._exp_layout.addWidget(self.rN, 1, 2, 1, 2) 
        self._exp_layout.addWidget(self.gain_e, 0, 2, 1, 2) 
        self._exp_layout.addWidget(self.gain_o, 0, 4, 1, 2) 
        self._exp_layout.addWidget(self.ncapture, 1, 4, 1, 2) 
        set_all_spacings(self._exp_layout)
        unifrom_layout_stretch(self._exp_layout, grid=True)

        # operation values
        operation_layout_colour = "rgb(66, 120, 139)"
        self._operation_layout = self.layout_bkg(main_layout=operation_layout, 
                                             panel_name="operation_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), 
                                             grid=True)
        self.init = QValueRangeWidget(name="Init", value=2.6, condition={"low":0,"high":np.inf}, border_colour=operation_layout_colour)
        self.train = QValueRangeWidget(name="Training", value=8.6, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self.setting = QValueRangeWidget(name="Setting", value=8.3, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self.start = QValueRangeWidget(name="Start", value=2.1, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self.stop = QValueRangeWidget(name="Stop", value=5.5, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self.stop2start = QValueRangeWidget(name="Start->Stop", value=2, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self.software = QValueRangeWidget(name="Software", value=2, condition={"low":2,"high":15}, border_colour=operation_layout_colour)
        self._operation_layout.addWidget(self.init, 0, 0, 1, 2) 
        self._operation_layout.addWidget(self.train, 0, 2, 1, 2) 
        self._operation_layout.addWidget(self.setting, 0, 4, 1, 2) 
        self._operation_layout.addWidget(self.start, 1, 0, 1, 2) 
        self._operation_layout.addWidget(self.stop, 1, 2, 1, 2) 
        self._operation_layout.addWidget(self.stop2start, 1, 4, 1, 2) 
        self._operation_layout.addWidget(self.software, 2, 2, 1, 2) 
        set_all_spacings(self._operation_layout)
        unifrom_layout_stretch(self._operation_layout, grid=True)

        # temperature values
        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout_colour = "rgb(166, 215, 208)"
        self._temp_layout = self.layout_bkg(main_layout=temp_layout, 
                                             panel_name="temp_panel", 
                                             style_sheet_string=self._layout_style("white", temp_layout_colour))
        self.fpga_temp = QValueRangeWidget(name="FPGA T", value=0, condition={"low":0,"high":np.inf}, border_colour=temp_layout_colour)
        self.sensor_temp = QValueRangeWidget(name="Sensor T", value=0, condition={"low":0,"high":np.inf}, border_colour=temp_layout_colour)
        self._temp_layout.addWidget(self.fpga_temp) 
        self._temp_layout.addWidget(self.sensor_temp) 
        set_all_spacings(self._temp_layout)
        # unifrom_layout_stretch(exp_layout, grid=True)

        # photon 
        phot_layout = QtWidgets.QVBoxLayout()
        phot_layout_colour = "rgba(92, 183, 182, 150)"
        self._phot_layout = self.layout_bkg(main_layout=phot_layout, 
                                             panel_name="phot_panel", 
                                             style_sheet_string=self._layout_style("white", phot_layout_colour))
        self.ph_w = QValueRangeWidget(name="Whole Ph. R.", value=0, condition={"low":0,"high":np.inf}, border_colour=phot_layout_colour)
        self.ph_p = QValueRangeWidget(name="Part Ph. R.", value=0, condition={"low":0,"high":np.inf}, border_colour=phot_layout_colour)
        self._phot_layout.addWidget(self.ph_w) 
        self._phot_layout.addWidget(self.ph_p) 
        set_all_spacings(self._phot_layout)

        # computer
        comp_layout = QtWidgets.QVBoxLayout()
        comp_layout_colour = "rgb(200, 194, 187)"
        self._comp_layout = self.layout_bkg(main_layout=comp_layout, 
                                             panel_name="comp_panel", 
                                             style_sheet_string=self._layout_style("white", comp_layout_colour))
        self.cpu = QValueRangeWidget(name="CPU Load Ave.", value=0, condition={"low":0,"high":np.inf}, border_colour=comp_layout_colour)
        self.mem = QValueRangeWidget(name="Disk Space", value=0, condition={"low":0,"high":np.inf}, border_colour=comp_layout_colour)
        self._comp_layout.addWidget(self.cpu) 
        self._comp_layout.addWidget(self.mem)
        set_all_spacings(self._comp_layout)

        # write status
        write_layout = QtWidgets.QVBoxLayout()
        write_layout_colour = "rgb(88, 189, 186)"
        self._write_layout = self.layout_bkg(main_layout=write_layout, 
                                             panel_name="write_panel", 
                                             style_sheet_string=self._layout_style(write_layout_colour, write_layout_colour))
        self.pointer = QValueRangeWidget(name="Write Pointer", value=0, condition={"low":0,"high":np.inf}, border_colour=write_layout_colour)
        self._write_layout.addWidget(self.pointer) 
        set_all_spacings(self._write_layout)

        # more exposure
        xexp_layout = QtWidgets.QVBoxLayout()
        xexp_layout_colour = "rgb(141, 141, 134)"
        self._xexp_layout = self.layout_bkg(main_layout=xexp_layout, 
                                             panel_name="xexp_panel", 
                                             style_sheet_string=self._layout_style("white", xexp_layout_colour))
        self.expxx = QValueRangeWidget(name="Ch. Exp. XX", value=0, condition={"low":0,"high":np.inf}, border_colour=xexp_layout_colour)
        self.exp192 = QValueRangeWidget(name="Ch. Exp. 192", value=0, condition={"low":0,"high":np.inf}, border_colour=xexp_layout_colour)
        self._xexp_layout.addWidget(self.expxx) 
        self._xexp_layout.addWidget(self.exp192)
        set_all_spacings(self._xexp_layout)

        self.ql.reader.value_changed_collection.connect(self.all_ql_fields)
        self.pc.reader.value_changed_collection.connect(self.all_pc_fields)

        ## all widgets together
        # image
        global_layout = QGridLayout()
        # global_layout.addWidget(self.image, 0, 0, 4, 4)
        global_layout.addLayout(ql_layout, 0, 0, 40, 43)#,43
                                #alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop) # y,x,h,w
        # pedestal
        # global_layout.addWidget(self.ped, 4, 0, 4, 3)
        global_layout.addLayout(pc_layout, 0, 43, 18, 36)#,
                                #alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)# y,x,h,w
        
        global_layout.addLayout(temp_layout, 40, 0, 10, 22)
        global_layout.addLayout(phot_layout, 40, 22, 10, 21)
        # global_layout.addLayout(comp_layout, 40, 29, 10, 14)
        global_layout.addLayout(exp_layout, 18, 43, 16, 57)#,
                                #alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom)
        global_layout.addLayout(operation_layout, 34, 43, 16, 57)
        global_layout.addLayout(xexp_layout, 9, 79, 9, 21)
        global_layout.addLayout(comp_layout, 0, 79, 9, 21)
        global_layout.addLayout(write_layout, 45, 82, 5, 18) #last since it overlaps with operation_layout

        unifrom_layout_stretch(global_layout, grid=True)

        # image_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._ql_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        # ped_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._pc_layout.setContentsMargins(0, 0, 0, 0)
        self._temp_layout.setContentsMargins(0, 0, 0, 0)
        self._phot_layout.setContentsMargins(0, 0, 0, 0)
        self._exp_layout.setContentsMargins(0, 0, 0, 0)
        self._write_layout.setContentsMargins(0, 0, 0, 0)
        self._operation_layout.setContentsMargins(0, 0, 0, 0)
        self._xexp_layout.setContentsMargins(0, 0, 0, 0)
        self._comp_layout.setContentsMargins(0, 0, 0, 0)
        # self._exp_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)

    def all_ql_fields(self):
        """ 
        Update the:
        * gain field, 
        * exposure
        """
        self.exp_ql.update_label(self.ql.reader.collection.get_exposure())

    def all_pc_fields(self):
        """ 
        Update the:
        * count rate field, 
        """
        self.exp_pc.update_label(self.pc.reader.collection.get_exposure())

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
    def __init__(self, cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1):
        super().__init__()     
        
        # self.setGeometry(100,100,2000,350)
        self.detw, self.deth = 2000,500
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(600,150)
        self.setWindowTitle("All CdTe View")
        self.aspect_ratio = self.detw/self.deth

        # data_file_pc = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
        # data_file_ql = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL

        f0 = CMOSWidget(data_file_pc=cmos_pc0, data_file_ql=cmos_ql0, name=os.path.basename(cmos_pc0))
        # f0.resize(QtCore.QSize(150, 190))
        _f0 =QHBoxLayout()
        _f0.addWidget(f0)

        f1 = CMOSWidget(data_file_pc=cmos_pc1, data_file_ql=cmos_ql1, name=os.path.basename(cmos_pc1))
        # f1.resize(QtCore.QSize(150, 150))
        _f1 =QGridLayout()
        _f1.addWidget(f1, 0, 0)

        lay = QGridLayout(spacing=0)
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

        # lay.addWidget(f0, 0, 0, 1, 1)
        # lay.addWidget(f1, 0, 1, 1, 1)
        lay.addLayout(_f0, 0, 0, 1, 1)
        lay.addLayout(_f1, 0, 1, 1, 1)

        unifrom_layout_stretch(lay, grid=True)

        lay.setContentsMargins(1, 1, 1, 1) # left, top, right, bottom
        lay.setHorizontalSpacing(0)
        lay.setVerticalSpacing(0)
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
    
    
    cmos_pc0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
    cmos_ql0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL
    cmos_pc1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
    cmos_ql1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL

    
    cmos_pc0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos1_pc.log"
    cmos_ql0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos1_ql.log"
    cmos_pc1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos2_pc.log"
    cmos_ql1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos2_ql.log"
    
    # w.resize(1000,500)
    w = AllCMOSView(cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1)
    # w = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql)
    
    w.show()
    app.exec()