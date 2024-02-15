"""
A widget to show off CdTe data.
"""
import os

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,QBoxLayout

from FoGSE.read_raw_to_refined.readRawToRefinedCdTe import CdTeReader
from FoGSE.windows.CdTeWindow import CdTeWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget, QValueWidget, QValueTimeWidget, QValueCheckWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.widgets.layout_tools.spacing import set_all_spacings


class CdTeWidget(QWidget):
    """
    An individual window to display CdTe data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.read_raw_to_refined.readRawToRefinedCdTe.CdTeReader()`.
        Default: None

    plotting_product : `str`
        String to determine whether an "image" and or "spectrogram" should be shown.
        Default: "image"
    """
    def __init__(self, data_file=None, name="CdTe", image_angle=0, parent=None):

        QWidget.__init__(self, parent)
        reader = CdTeReader(datafile=data_file)

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 50, 50
        self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts for the status window, LED, buttons, times, and plot
        image_layout = QtWidgets.QGridLayout()
        ped_layout = QtWidgets.QGridLayout()
        value_layout = QtWidgets.QVBoxLayout()

        self.panels = dict() # for all the background panels
        
        ## for CdTe image
        # widget for displaying the automated recommendation
        self._image_layout = self.layout_bkg(main_layout=image_layout, 
                                             panel_name="image_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.image = CdTeWindow(reader=reader, plotting_product="image", name=name, integrate=True, image_angle=image_angle)#, integrate=True
        self.image.setStyleSheet("border-width: 0px;")
        self._image_layout.addWidget(self.image)

        ## for CdTe pedestal
        # widget for displaying the automated recommendation
        self._ped_layout = self.layout_bkg(main_layout=ped_layout, 
                                             panel_name="ped_panel", 
                                             style_sheet_string=self._layout_style("white", "white"), grid=True)
        self.ped = CdTeWindow(reader=reader, plotting_product="spectrogram", name="", integrate=True, image_angle=image_angle)
        self.lc = CdTeWindow(reader=reader, plotting_product="lightcurve", name="")
        self.ped.setStyleSheet("border-width: 0px;")
        self._ped_layout.addWidget(self.ped) 
        self.ped_layout = ped_layout

        self.ped.mousePressEvent = self._switch2lc
        self.lc.mousePressEvent = self._switch2ped

        # status values
        self._value_layout = self.layout_bkg(main_layout=value_layout, 
                                             panel_name="value_panel", 
                                             style_sheet_string=self._layout_style("white", "white"))
        # de
        de_layout = QtWidgets.QGridLayout()
        de_layout_colour = "rgb(53, 108, 117)"
        self.software_stat = QValueTimeWidget(name="SW Status", 
                                              value="N/A", 
                                              time=2000, 
                                              condition=[int, float, np.int64], 
                                              border_colour=de_layout_colour,
                                              tool_tip_values={"ASIC VTH":QValueWidget(name="ASIC VTH", value="N/A"), 
                                                               "ASIC DTH":QValueWidget(name="ASIC DTH", value="N/A"), 
                                                               "ASIC Load":QValueWidget(name="ASIC Load", value="N/A")},
                                              name_plus="<sup>*</sup>")
        self.de_mode = QValueRangeWidget(name="DE mode", value="N/A", condition={"low":0,"high":np.inf}, border_colour=de_layout_colour)
        self.ping = QValueCheckWidget(name="Ping", value="N/A", condition={"acceptable":[("", "white")]}, border_colour=de_layout_colour)
        self.hv = QValueRangeWidget(name="HV", value="N/A", condition={"low":0,"high":200}, border_colour=de_layout_colour)
        de_layout.addWidget(self.software_stat, 0, 0, 1, 2) 
        de_layout.addWidget(self.de_mode, 1, 0, 1, 2) 
        de_layout.addWidget(self.ping, 2, 0, 1, 2) 
        de_layout.addWidget(self.hv, 3, 0, 1, 2) 
        # counts
        cts_layout = QtWidgets.QGridLayout()
        cts_layout_colour = "rgb(141, 141, 134)"
        self.cts = QValueRangeWidget(name="<span>&#931;</span> Ct", 
                                     value="N/A", 
                                     condition={"low":0,"high":np.inf}, 
                                     border_colour=cts_layout_colour,
                                     tool_tip_values={"Ct Now":"N/A", "Ct Mean":"N/A", "Ct Median":"N/A", "Ct Max.":"N/A", "Ct Min.":"N/A"},
                                     name_plus="<sup>*</sup>")
        self.ctr = QValueRangeWidget(name="<span>&#931;</span> Ct/s", 
                                     value="N/A", 
                                     condition={"low":0,"high":np.inf}, 
                                     border_colour=cts_layout_colour,
                                     tool_tip_values={"Ct Now":"N/A", "Ct Mean":"N/A", "Ct Median":"N/A", "Ct Max.":"N/A", "Ct Min.":"N/A"},
                                     name_plus="<sup>*</sup>")
        cts_layout.addWidget(self.cts, 0, 0, 1, 2) 
        cts_layout.addWidget(self.ctr, 1, 0, 1, 2) 
        # strips
        strips_layout = QtWidgets.QGridLayout()
        strips_layout_colour = "rgb(213, 105, 48)"
        self.strips = QValueWidget(name="# of det. strips", value="", separator="", border_colour=strips_layout_colour)
        self.strips_al = QValueRangeWidget(name="Pt", value=0, condition={"low":0,"high":127}, border_colour=strips_layout_colour)
        self.strips_pt = QValueRangeWidget(name="Al", value=0, condition={"low":0,"high":127}, border_colour=strips_layout_colour)
        strips_layout.addWidget(self.strips, 0, 0, 1, 2) 
        strips_layout.addWidget(self.strips_pt, 1, 0, 1, 1) 
        strips_layout.addWidget(self.strips_al, 1, 1, 1, 1) 
        # frames
        frames_layout = QtWidgets.QGridLayout()
        frames_layout_colour = "rgb(66, 120, 139)"
        self.frames = QValueWidget(name="# of rest evt. frame", value="", separator="", border_colour=frames_layout_colour)
        self.frames_t = QValueRangeWidget(name="t", value=0, condition={"low":0,"high":127}, border_colour=frames_layout_colour)
        self.frames_tm1 = QValueRangeWidget(name="t-1", value=0, condition={"low":0,"high":127}, border_colour=frames_layout_colour)
        frames_layout.addWidget(self.frames, 0, 0, 1, 2) 
        frames_layout.addWidget(self.frames_t, 1, 0, 1, 1) 
        frames_layout.addWidget(self.frames_tm1, 1, 1, 1, 1)
        
        
        self._value_layout.addLayout(de_layout) 

        self._value_layout.addLayout(cts_layout) 
        
        self._value_layout.addLayout(strips_layout) 
        self._value_layout.addLayout(frames_layout)
        set_all_spacings(self._value_layout)

        self.image.reader.value_changed_collection.connect(self.all_fields)

        ## all widgets together
        # image
        global_layout = QGridLayout()
        global_layout.addLayout(image_layout, 0, 0, 4, 4)
        global_layout.addLayout(ped_layout, 4, 0, 2, 4)
        global_layout.addLayout(value_layout, 0, 4, 6, 2)

        unifrom_layout_stretch(global_layout, grid=True)

        self._image_layout.setContentsMargins(0, 0, 0, 0) # left, top, right, bottom
        self._ped_layout.setContentsMargins(0, 0, 0, 0)
        self._value_layout.setContentsMargins(0, 0, 0, 0)
        self._value_layout.setSpacing(6)
        strips_layout.setSpacing(0)
        frames_layout.setSpacing(0)
        de_layout.setSpacing(0)
        cts_layout.setSpacing(0)
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
        total_counts = self.image.reader.collection.total_counts()
        self.cts.update_label(total_counts)
        _lc_info = self._get_lc_info()
        print("sadgfs", _lc_info)
        self.cts.update_tool_tip({"Ct Now":total_counts, 
                                  "Ct Mean":_lc_info["Ct Mean"], 
                                  "Ct Median":_lc_info["Ct Median"], 
                                  "Ct Max.":_lc_info["Ct Max."], 
                                  "Ct Min.":_lc_info["Ct Min."]})
        
    def _get_lc_info(self):
        """ To update certain fields, we look to the lightcurve information. """
        if len(self.lc.graphPane.plot_data)<2:
            return {"Ct Mean":"N/A",
                    "Ct Median":"N/A", 
                    "Ct Max.":"N/A", 
                    "Ct Min.":"N/A"}
        elif len(self.lc.graphPane.plot_data)==2:
            lc_data = self.lc.graphPane.plot_data[1:] 
        else:
            lc_data = self.lc.graphPane.plot_data

        return {"Ct Mean":np.nanmean(lc_data),
                "Ct Median":np.nanmedian(lc_data), 
                "Ct Max.":np.nanmax(lc_data), 
                "Ct Min.":np.nanmin(lc_data)}
        
    def _switch2lc(self, event=None):
        self._ped_layout.removeWidget(self.ped) 
        self.ped_layout.removeWidget(self.ped) 
        self._ped_layout.addWidget(self.lc) 
        self.ped_layout.addWidget(self.lc) 

    def _switch2ped(self, event=None):
        self._ped_layout.removeWidget(self.lc) 
        self.ped_layout.removeWidget(self.lc) 
        self._ped_layout.addWidget(self.ped) 
        self.ped_layout.addWidget(self.ped) 

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

        f0 = CdTeWidget(data_file=cdte0, name=os.path.basename(cdte0), image_angle=-150)
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
        
        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)

if __name__=="__main__":
    app = QApplication([])

    # different data files to try
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2022_03/NiFoilAm241/10min/test_20230609a_det03_00012_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Am241/test_berk_20230803_proto_Am241_1min_postvibe2_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/fromBerkeley_postVibeCheckFiles/Fe55/test_berk_20230803_proto_Fe55_1min__postvibe2_00008_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Am241/1min/test_berk_20230728_det05_00005_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Fe55/1min/test_berk_20230728_det05_00006_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeImages/no2021_05/Cr51/1min/test_berk_20230728_det05_00007_001"
    # datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/berkeley/prototype_vibe_test/vibetest_presinez_berk_20230802_proto_00012_001"
    
    # import os
    # FILE_DIR = os.path.dirname(os.path.realpath(__file__))
    # datafile = FILE_DIR+"/../data/test_berk_20230728_det05_00007_001"
    # datafile = "/Users/kris/Desktop/test_230306_00001_001_nohk"
    # datafile="/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/calibration/j-sideRootData/usingDAQ/raw2root/backgrounds-20230331-newGrounding/20230331_bkg_00001_001"
    # # datafile = "/Users/kris/Desktop/cdte_20231030.log"
    # # datafile = "/Users/kris/Desktop/cdte_20231030_postsend.log"
    # # datafile = "/Users/kris/Desktop/cdte_20231030_presend.log"
    # datafile = "/Users/kris/Desktop/cdte_20231030_fullread.log"
    # datafile = "/Users/kris/Desktop/cdte_src_mod.log"
    # datafile = "/Users/kris/Desktop/gse_mod.log"
    # datafile = "/Users/kris/Desktop/from_de.log"
    # # datafile = "/Users/kris/Desktop/from_gse.log"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeTrialsOfParser-20231102/cdte.log"
    # # datafile = ""

    # # `datafile = FILE_DIR+"/../data/cdte.log"`
    # reader = CdTeFileReader(datafile)#CdTeReader(data_file)
    # # reader = CdTeReader(datafile)
    
    # f0 = CdTeWidget(data_file=datafile)
    # _f0 =QGridLayout()
    # _f0.addWidget(f0, 0, 0)

    # f1 = CdTeWidget(data_file=datafile)
    # _f1 =QGridLayout()
    # _f1.addWidget(f1, 0, 0)

    # f2 = CdTeWidget(data_file=datafile)
    # _f2 =QGridLayout()
    # _f2.addWidget(f2, 0, 0)

    # f3 = CdTeWidget(data_file=datafile)
    # _f3 =QGridLayout()
    # _f3.addWidget(f3, 0, 0)
    
    # w = QWidget()
    # lay = QGridLayout(w)
    # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

    # # lay.addWidget(f0, 0, 0, 1, 1)
    # # lay.addWidget(f1, 0, 1, 1, 1)
    # lay.addLayout(_f0, 0, 0, 1, 1)
    # lay.addLayout(_f1, 0, 1, 1, 1)
    # lay.addLayout(_f2, 0, 2, 1, 1)
    # lay.addLayout(_f3, 0, 3, 1, 1)

    cdte0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeTrialsOfParser-20231102/cdte.log"
    cdte1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte2.log"
    cdte2 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte3.log"
    cdte3 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte4.log"
    
    # w.resize(1000,500)
    w = AllCdTeView(cdte0, cdte1, cdte2, cdte3)
    # w = CdTeWidget(data_file=datafile)
    
    w.show()
    app.exec()