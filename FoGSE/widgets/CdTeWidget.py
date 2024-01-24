"""
A demo to walk through an existing CdTe raw file.
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QGridLayout

from FoGSE.read_raw_to_refined.readRawToRefinedCdTe import CdTeReader
from FoGSE.windows.CdTewindow import CdTeWindow
from FoGSE.widgets.QValueWidget import QValueRangeWidget


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
    def __init__(self, data_file=None, image_angle=0, name="CdTe", parent=None):

        QWidget.__init__(self, parent)
        reader = CdTeReader(datafile=data_file)

        self.setWindowTitle(f"{name}")
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")
        self.detw, self.deth = 500, 500
        self.setMinimumSize(self.detw, self.deth) # stops the panel from stretching and squeezing when changing times
        self.aspect_ratio = self.detw/self.deth

        # define main layouts for the status window, LED, buttons, times, and plot
        image_layout = QtWidgets.QGridLayout()
        ped_layout = QtWidgets.QGridLayout()
        value_layout = QtWidgets.QGridLayout()

        self.panels = dict() # for all the background panels
        
        ## for CdTe image
        # widget for displaying the automated recommendation
        # self._image_layout = self.layout_bkg(main_layout=image_layout, 
        #                                      panel_name="image_panel", 
        #                                      style_sheet_string=self._layout_style("grey", "white"))
        self.image = CdTeWindow(reader=reader, plotting_product="image")
        # self.image.setMinimumSize(QtCore.QSize(400,400)) # was 250,250
        # self.image.setStyleSheet("border-width: 0px;")
        # self._image_layout.addWidget(self.image)
        # image_layout.addWidget(self.image)

        ## for CdTe pedestal
        # widget for displaying the automated recommendation
        # self._ped_layout = self.layout_bkg(main_layout=ped_layout, 
        #                                      panel_name="ped_panel", 
        #                                      style_sheet_string=self._layout_style("grey", "white"))
        self.ped = CdTeWindow(reader=reader, plotting_product="spectrogram")
        # self.image.setMinimumSize(QtCore.QSize(400,200)) # was 250,250
        # self.ped.setStyleSheet("border-width: 0px;")
        # self._ped_layout.addWidget(self.ped) 

        # status values
        # self._value_layout = self.layout_bkg(main_layout=value_layout, 
        #                                      panel_name="value_panel", 
        #                                      style_sheet_string=self._layout_style("grey", "white"))
        self.somevalue0 = QValueRangeWidget(name="This", value=6, condition={"low":2,"high":15})
        self.somevalue1 = QValueRangeWidget(name="That", value=8, condition={"low":2,"high":15})
        self.somevalue2 = QValueRangeWidget(name="Other", value=60, condition={"low":2,"high":15})
        self.somevalue3 = QValueRangeWidget(name="Another", value="8", condition={"low":2,"high":15})
        self.somevalue4 = QValueRangeWidget(name="Again", value=2, condition={"low":2,"high":15})
        self.somevalue5 = QValueRangeWidget(name="This2", value=14, condition={"low":2,"high":15})
        # self._value_layout.addWidget(self.somevalue0) 
        # self._value_layout.addWidget(self.somevalue1) 
        # self._value_layout.addWidget(self.somevalue2) 
        # self._value_layout.addWidget(self.somevalue3) 
        # self._value_layout.addWidget(self.somevalue4) 
        # self._value_layout.addWidget(self.somevalue5) 

        ## all widgets together
        # image
        global_layout = QGridLayout()
        global_layout.addWidget(self.image, 0, 0, 40, 40)
        # pedestal
        global_layout.addWidget(self.ped, 35, 0, 20, 40)
        # status values
        global_layout.addWidget(self.somevalue0, 0, 38, 10, 15)
        global_layout.addWidget(self.somevalue1, 8, 38, 10, 15)
        global_layout.addWidget(self.somevalue2, 16, 38, 10, 15)
        global_layout.addWidget(self.somevalue3, 24, 38, 10, 15)
        global_layout.addWidget(self.somevalue4, 32, 38, 10, 15)
        global_layout.addWidget(self.somevalue5, 40, 38, 10, 15)
        # global_layout.addLayout(value_layout, 0, 4, 6, 1)

        # actually display the layout
        self.setLayout(global_layout)
        
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
        return f"border-width: 2px; border-style: outset; border-radius: 10px; border-color: {border_colour}; background-color: {background_colour};"
    
    def update_aspect(self, aspect_ratio):
        """ Update the image aspect ratio (width/height). """
        self.aspect_ratio = aspect_ratio

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        
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
    
    f0 = CdTeWidget(data_file=datafile)
    _f0 =QGridLayout()
    _f0.addWidget(f0, 0, 0)

    f1 = CdTeWidget(data_file=datafile)
    _f1 =QGridLayout()
    _f1.addWidget(f1, 0, 0)

    f2 = CdTeWidget(data_file=datafile)
    _f2 =QGridLayout()
    _f2.addWidget(f2, 0, 0)

    f3 = CdTeWidget(data_file=datafile)
    _f3 =QGridLayout()
    _f3.addWidget(f3, 0, 0)
    
    w = QWidget()
    lay = QGridLayout(w)
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: white;")

    # lay.addWidget(f0, 0, 0, 1, 1)
    # lay.addWidget(f1, 0, 1, 1, 1)
    lay.addLayout(_f0, 0, 0, 1, 1)
    lay.addLayout(_f1, 0, 1, 1, 1)
    lay.addLayout(_f2, 0, 2, 1, 1)
    lay.addLayout(_f3, 0, 3, 1, 1)
    
    w.resize(1000,500)
    w.show()
    app.exec()