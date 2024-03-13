"""
A widget to show off CMOS data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.read_raw_to_refined.readRawToRefinedCMOSPC import CMOSPCReader
from FoGSE.read_raw_to_refined.readRawToRefinedCMOSQL import CMOSQLReader
from FoGSE.read_raw_to_refined.readRawToRefinedCMOSHK import CMOSHKReader
from FoGSE.windows.CMOSPCWindow import CMOSPCWindow
from FoGSE.windows.CMOSQLWindow import CMOSQLWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget, QValueWidget, QValueChangeWidget, QValueTimeWidget, QValueCheckWidget, QValueMultiRangeWidget
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
    def __init__(self, data_file_pc=None, data_file_ql=None, data_file_hk=None, name="CMOS", image_angle=0, parent=None):

        QWidget.__init__(self, parent)
        reader_pc = CMOSPCReader(datafile=data_file_pc)
        reader_ql = CMOSQLReader(datafile=data_file_ql)
        self.reader_hk = CMOSHKReader(datafile=data_file_hk)

        self._default_qvaluewidget_value = "<span>&#129418;</span>" #fox

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
        self.ql = CMOSQLWindow(reader=reader_ql, plotting_product="image", name=name, integrate=True, image_angle=image_angle)
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
        self.pc = CMOSPCWindow(reader=reader_pc, plotting_product="image", name=name, integrate=True, image_angle=0)#image_angle)
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
        self.gain_m = QValueCheckWidget(name="Gain Mode", value=self._default_qvaluewidget_value, condition={"acceptable":[(2,"white")]}, border_colour=exp_layout_colour)
        self.exp_ql = QValueRangeWidget(name="QL Exp.", value=self._default_qvaluewidget_value, condition={"low":1,"high":192}, border_colour=exp_layout_colour)
        self.exp_pc = QValueRangeWidget(name="PC Exp.", value=self._default_qvaluewidget_value, condition={"low":1,"high":192}, border_colour=exp_layout_colour)
        self.rn = QValueCheckWidget(name="Repeat \"n\"", value=self._default_qvaluewidget_value, condition={"acceptable":[(50,"white")]}, border_colour=exp_layout_colour)
        self.rN = QValueCheckWidget(name="Repeat \"N\"", value=self._default_qvaluewidget_value, condition={"acceptable":[(1,"white")]}, border_colour=exp_layout_colour)
        self.gain_e = QValueCheckWidget(name="Gain Even", value=self._default_qvaluewidget_value, condition={"acceptable":[(3,"white")]}, border_colour=exp_layout_colour)
        self.gain_o = QValueCheckWidget(name="Gain Odd", value=self._default_qvaluewidget_value, condition={"acceptable":[(3,"white")]}, border_colour=exp_layout_colour)
        self.ncapture = QValueCheckWidget(name="NCapture", value=self._default_qvaluewidget_value, condition={"acceptable":[(65534,"white")]}, border_colour=exp_layout_colour) 
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
        self.init = QValueRangeWidget(name="Init", value=self._default_qvaluewidget_value, condition={"low":1,"high":np.inf}, border_colour=operation_layout_colour)
        self.train = QValueRangeWidget(name="Training", value=self._default_qvaluewidget_value, condition={"low":1,"high":np.inf}, border_colour=operation_layout_colour)
        self.setting = QValueRangeWidget(name="Setting", value=self._default_qvaluewidget_value, condition={"low":1,"high":np.inf}, border_colour=operation_layout_colour)
        self.start = QValueRangeWidget(name="Start", value=self._default_qvaluewidget_value, condition={"low":1,"high":np.inf}, border_colour=operation_layout_colour)
        self.stop = QValueRangeWidget(name="Stop", value=self._default_qvaluewidget_value, condition={"low":1,"high":np.inf}, border_colour=operation_layout_colour)
        self.stop2start = QValueRangeWidget(name="Init->Stop", value=self._default_qvaluewidget_value, condition={"low":0,"high":np.inf}, border_colour=operation_layout_colour)
        self.software = QValueTimeWidget(name="SW Stat.", 
                                              value=self._default_qvaluewidget_value, 
                                              time=4000, 
                                              condition=[int, float, np.int64, str], 
                                          border_colour=operation_layout_colour,
                                          tool_tip_values={"Linetime":QValueWidget(name="Linetime", value=self._default_qvaluewidget_value), 
                                                           "Linetime @ pps":QValueWidget(name="Linetime @ pps", value=self._default_qvaluewidget_value), 
                                                           "QL DL Read Pointer":QValueChangeWidget(name="QL DL Read Pointer", value=self._default_qvaluewidget_value), 
                                                           "PC DL Read Pointer":QValueChangeWidget(name="PC DL Read Pointer", value=self._default_qvaluewidget_value)},
                                          name_plus="<sup>*</sup>")
        self._operation_layout.addWidget(self.init, 0, 0, 1, 2) 
        self._operation_layout.addWidget(self.train, 0, 2, 1, 2) 
        self._operation_layout.addWidget(self.setting, 0, 4, 1, 2) 
        self._operation_layout.addWidget(self.start, 1, 0, 1, 2) 
        self._operation_layout.addWidget(self.stop, 1, 2, 1, 2) 
        self._operation_layout.addWidget(self.stop2start, 1, 4, 1, 2) 
        self._operation_layout.addWidget(self.software, 2, 2, 1, 2) 
        write_layout_colour = "rgb(88, 189, 186)"
        self.pointer = QValueChangeWidget(name="Wr. P.", value=self._default_qvaluewidget_value, border_colour=write_layout_colour)
        self._operation_layout.addWidget(self.pointer, 2, 4, 1, 2) 
        set_all_spacings(self._operation_layout)
        unifrom_layout_stretch(self._operation_layout, grid=True)

        # temperature values
        temp_layout = QtWidgets.QVBoxLayout()
        temp_layout_colour = "rgb(166, 215, 208)"
        self._temp_layout = self.layout_bkg(main_layout=temp_layout, 
                                             panel_name="temp_panel", 
                                             style_sheet_string=self._layout_style("white", temp_layout_colour))
        self.fpga_temp = QValueRangeWidget(name="FPGA T", value=self._default_qvaluewidget_value, condition={"low":-np.inf,"high":np.inf}, border_colour=temp_layout_colour)
        self.sensor_temp = QValueRangeWidget(name="Sensor T", value=self._default_qvaluewidget_value, condition={"low":-np.inf,"high":np.inf}, border_colour=temp_layout_colour)
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
        self.ph_w = QValueRangeWidget(name="Whole Ph. R.", value=self._default_qvaluewidget_value, condition={"low":0,"high":np.inf}, border_colour=phot_layout_colour)
        self.ph_p = QValueRangeWidget(name="Part Ph. R.", value=self._default_qvaluewidget_value, condition={"low":0,"high":np.inf}, border_colour=phot_layout_colour)
        self._phot_layout.addWidget(self.ph_w) 
        self._phot_layout.addWidget(self.ph_p) 
        set_all_spacings(self._phot_layout)

        # computer
        comp_layout = QtWidgets.QVBoxLayout()
        comp_layout_colour = "rgb(200, 194, 187)"
        self._comp_layout = self.layout_bkg(main_layout=comp_layout, 
                                             panel_name="comp_panel", 
                                             style_sheet_string=self._layout_style("white", comp_layout_colour))
        cpu_cond = {"range1":[0,60,"white"], "range2":[60,100,"red"], "other":"orange", "error":"orange"}
        disk_cond = {"range1":[20,100,"white"], "range2":[0,20,"red"], "other":"orange", "error":"orange"}
        self.cpu = QValueMultiRangeWidget(name="CPU Load Ave.", value=self._default_qvaluewidget_value, condition=cpu_cond, border_colour=comp_layout_colour)
        self.mem = QValueMultiRangeWidget(name="Disk Space", value=self._default_qvaluewidget_value, condition=disk_cond, border_colour=comp_layout_colour)
        self._comp_layout.addWidget(self.cpu) 
        self._comp_layout.addWidget(self.mem)
        set_all_spacings(self._comp_layout)

        # more exposure
        xexp_layout = QtWidgets.QVBoxLayout()
        xexp_layout_colour = "rgb(141, 141, 134)"
        self._xexp_layout = self.layout_bkg(main_layout=xexp_layout, 
                                             panel_name="xexp_panel", 
                                             style_sheet_string=self._layout_style("white", xexp_layout_colour))
        self.expxx = QValueRangeWidget(name="Ch. Exp. XX", value=self._default_qvaluewidget_value, condition={"low":0,"high":np.inf}, border_colour=xexp_layout_colour)
        self.exp192 = QValueRangeWidget(name="Ch. Exp. 192", value=self._default_qvaluewidget_value, condition={"low":0,"high":np.inf}, border_colour=xexp_layout_colour)
        self._xexp_layout.addWidget(self.expxx) 
        self._xexp_layout.addWidget(self.exp192)
        set_all_spacings(self._xexp_layout)

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
        # global_layout.addLayout(write_layout, 45, 82, 5, 18) #last since it overlaps with operation_layout

        unifrom_layout_stretch(global_layout, grid=True)

        # image_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._ql_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        # ped_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._pc_layout.setContentsMargins(0, 0, 0, 0)
        self._temp_layout.setContentsMargins(0, 0, 0, 0)
        self._phot_layout.setContentsMargins(0, 0, 0, 0)
        self._exp_layout.setContentsMargins(0, 0, 0, 0)
        # self._write_layout.setContentsMargins(0, 0, 0, 0)
        self._operation_layout.setContentsMargins(0, 0, 0, 0)
        self._xexp_layout.setContentsMargins(0, 0, 0, 0)
        self._comp_layout.setContentsMargins(0, 0, 0, 0)
        # self._exp_layout.setContentsMargins(0, 0, 0, 0)
        global_layout.setHorizontalSpacing(0)
        global_layout.setVerticalSpacing(0)
        global_layout.setContentsMargins(0, 0, 0, 0)

        # actually display the layout
        self.setLayout(global_layout)


        self.pc.base_qwidget_entered_signal.connect(self.ql.add_pc_region)
        self.pc.base_qwidget_left_signal.connect(self.ql.remove_pc_region)

        self.pc.base_qwidget_entered_signal.connect(self.pc.add_arc_distances)
        self.pc.base_qwidget_left_signal.connect(self.pc.remove_arc_distances)
        self.ql.base_qwidget_entered_signal.connect(self.ql.add_arc_distances)
        self.ql.base_qwidget_left_signal.connect(self.ql.remove_arc_distances)

        # so the matplotlib ones work but aren't as reliable as the PyQt6 ones
        # self.pc.graphPane.mpl_axes_enter_signal.connect(self.ql.add_pc_region) 
        # self.pc.graphPane.mpl_axes_leave_signal.connect(self.ql.remove_pc_region)

        self.ql.reader.value_changed_collection.connect(self.all_ql_fields)
        self.pc.reader.value_changed_collection.connect(self.all_pc_fields)
        self.reader_hk.value_changed_collection.connect(self.all_hk_fields)

    def all_ql_fields(self):
        """ 
        Update the:
        * gain field, 
        * exposure
        """
        # self.exp_ql.update_label(self.ql.reader.collection.get_exposure())
        pass

    def all_pc_fields(self):
        """ 
        Update the:
        * count rate field, 
        """
        # self.exp_pc.update_label(self.pc.reader.collection.get_exposure())
        self.ph_w.update_label(round(self.pc.reader.collection.get_whole_photon_rate(),3))
        # self.ph_p.update_label("<span>&#129418;</span>")

    def all_hk_fields(self):
        """ Update the HK QValueWidgets. """

        # other methods of self.reader_hk.collection
        # get_error_time, get_error_flag, get_error_training, get_data_validity, get_data_size_QL, get_data_size_PC
        # print("ds",self.reader_hk.collection.get_data_size_PC())

        # ... = self.reader_hk.collection.something()
        self.gain_m.update_label(self.reader_hk.collection.get_gain_mode())
        self.exp_ql.update_label(self.reader_hk.collection.get_exposureQL())
        self.exp_pc.update_label(self.reader_hk.collection.get_exposurePC())
        self.rn.update_label(self.reader_hk.collection.get_repeat_n())
        self.rN.update_label(self.reader_hk.collection.get_repeat_N())
        self.gain_e.update_label(self.reader_hk.collection.get_gain_even())
        self.gain_o.update_label(self.reader_hk.collection.get_gain_odd())
        self.ncapture.update_label(self.reader_hk.collection.get_ncapture())

        self.init.update_label(self.reader_hk.collection.get_cmos_init())
        self.train.update_label(self.reader_hk.collection.get_cmos_training())
        self.setting.update_label(self.reader_hk.collection.get_cmos_setting())
        self.start.update_label(self.reader_hk.collection.get_cmos_start())
        self.stop.update_label(self.reader_hk.collection.get_cmos_stop())
        self.stop2start.update_label(self.reader_hk.collection.get_cmos_stop()-self.reader_hk.collection.get_cmos_init())
        self.software.update_label(self.reader_hk.collection.get_software_status())
        self.software.update_tool_tip({"Linetime":self.reader_hk.collection.get_line_time(), 
                                       "Linetime @ pps":self.reader_hk.collection.get_line_time_at_pps(), 
                                       "QL DL Read Pointer":self.reader_hk.collection.get_read_pointer_position_QL(), 
                                       "PC DL Read Pointer":self.reader_hk.collection.get_read_pointer_position_PC()})

        self.fpga_temp.update_label(round(self.reader_hk.collection.get_fpga_temp(),1))
        self.sensor_temp.update_label(round(self.reader_hk.collection.get_sensor_temp(),1))

        self.cpu.update_label(self.reader_hk.collection.get_cpu_load_average())
        self.mem.update_label(self.reader_hk.collection.get_remaining_disk_size())

        # self.expxx.update_label("<span>&#129418;</span>")
        # self.exp192.update_label("<span>&#129418;</span>")

        self.pointer.update_label(self.reader_hk.collection.get_write_pointer_position_store_data())

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
    def __init__(self, cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1, cmos_hk0=None, cmos_hk1=None):
        super().__init__()     
        
        # self.setGeometry(100,100,2000,350)
        self.detw, self.deth = 2000,500
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(600,150)
        self.setWindowTitle("All CdTe View")
        self.aspect_ratio = self.detw/self.deth

        # data_file_pc = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
        # data_file_ql = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL

        _reflection = -180 # degrees

        f0 = CMOSWidget(data_file_pc=cmos_pc0, data_file_ql=cmos_ql0, data_file_hk=cmos_hk0, name=os.path.basename(cmos_pc0), image_angle=180+_reflection)
        # f0.resize(QtCore.QSize(150, 190))
        _f0 =QHBoxLayout()
        _f0.addWidget(f0)

        f1 = CMOSWidget(data_file_pc=cmos_pc1, data_file_ql=cmos_ql1, data_file_hk=cmos_hk1, name=os.path.basename(cmos_pc1), image_angle=180+_reflection)
        # f1.resize(QtCore.QSize(150, 150))
        _f1 =QGridLayout()
        _f1.addWidget(f1, 0, 0)

        lay = QGridLayout(spacing=0)
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

        lay.addLayout(_f0, 0, 0, 1, 1)
        lay.addLayout(_f1, 0, 1, 1, 1)

        unifrom_layout_stretch(lay, grid=True)

        lay.setContentsMargins(1, 1, 1, 1) # left, top, right, bottom
        lay.setHorizontalSpacing(0)
        lay.setVerticalSpacing(0)
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        self.setLayout(lay)

        f0.ql.base_qwidget_entered_signal.connect(f0.ql.add_pc_region)
        f0.ql.base_qwidget_entered_signal.connect(f1.ql.add_pc_region)
        # f0.ql.add_box_signal.connect(f1.ql.add_rotate_frame)
        
        f0.ql.base_qwidget_left_signal.connect(f0.ql.remove_pc_region)
        f0.ql.base_qwidget_left_signal.connect(f1.ql.remove_pc_region)
        # f0.ql.remove_box_signal.connect(f1.ql.remove_rotate_frame)

        f1.ql.base_qwidget_entered_signal.connect(f0.ql.add_pc_region)
        f1.ql.base_qwidget_entered_signal.connect(f1.ql.add_pc_region)
        # f1.ql.add_box_signal.connect(f0.ql.add_pc_region)
        # f1.ql.add_box_signal.connect(f0.ql.add_rotate_frame)

        f1.ql.base_qwidget_left_signal.connect(f0.ql.remove_pc_region)
        f1.ql.base_qwidget_left_signal.connect(f1.ql.remove_pc_region)
        #f1.ql.remove_box_signal.connect(f0.ql.remove_pc_region)
        # f1.ql.remove_box_signal.connect(f0.ql.remove_rotate_frame)

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
    
    cmos_pc0 = "/Users/kris/Downloads/PC_check_downlink_new.dat"
    cmos_ql0 = "/Users/kris/Downloads/QL_check_downlink_new.dat"
    cmos_pc1 = "/Users/kris/Downloads/PC_check_downlink_new.dat"
    cmos_ql1 = "/Users/kris/Downloads/QL_check_downlink_new.dat"
    
    
    # w.resize(1000,500)
    w = AllCMOSView(cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1)
    # w = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql)
    
    w.show()
    app.exec()