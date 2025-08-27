"""
A widget to show off CdTe data.
"""
import os

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QGridLayout

from FoGSE.widgets.CdTeWidget import CdTeWidget
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch


class AllCdTeView(QWidget):
    def __init__(self, cdte0, cdte1, cdte2, cdte3):
        super().__init__()     
        
        # self.setGeometry(100,100,2000,350)
        self.detw, self.deth = 2300,500
        self.setGeometry(100,100,self.detw, self.deth)
        self.setMinimumSize(600,150)
        self.setWindowTitle("All CdTe View")
        self.aspect_ratio = self.detw/self.deth

        # datafile0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/CdTeTrialsOfParser-20231102/cdte.log"
        # datafile1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte2.log"
        # datafile2 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte3.log"
        # datafile3 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/preWSMRship/Jan24-gse_filter/cdte4.log"

        _reflection = -180 # degrees

        cdte_widget = self.get_cdte_widget()

        self.f0 = cdte_widget(data_file_pc=cdte0[0], data_file_hk=cdte0[1], data_file_de=cdte0[2], name=os.path.basename(cdte0[0]), image_angle=150+_reflection, ping_ind=0)
        # f0.resize(QtCore.QSize(150, 190))
        _f0 =QHBoxLayout()
        _f0.addWidget(self.f0)

        self.f1 = cdte_widget(data_file_pc=cdte1[0], data_file_hk=cdte1[1], data_file_de=cdte1[2], name=os.path.basename(cdte1[0]), image_angle=30+_reflection, ping_ind=1)
        # f1.resize(QtCore.QSize(150, 150))
        _f1 =QGridLayout()
        _f1.addWidget(self.f1, 0, 0)

        self.f2 = cdte_widget(data_file_pc=cdte2[0], data_file_hk=cdte2[1], data_file_de=cdte2[2], name=os.path.basename(cdte2[0]), image_angle=90+_reflection, ping_ind=2)
        # f2.resize(QtCore.QSize(150, 150))
        _f2 =QGridLayout()
        _f2.addWidget(self.f2, 0, 0)

        self.f3 = cdte_widget(data_file_pc=cdte3[0], data_file_hk=cdte3[1], data_file_de=cdte3[2], name=os.path.basename(cdte3[0]), image_angle=-30+_reflection, ping_ind=3)
        # f3.resize(QtCore.QSize(150, 150))
        _f3 =QGridLayout()
        _f3.addWidget(self.f3, 0, 0)

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
        unifrom_layout_stretch(lay, grid=True)
        self.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        self.setLayout(lay)

    def get_cdte_widget(self):
        """ A way the class can be inherited from but use different parsers. """
        return CdTeWidget

    def resizeEvent(self,event):
        """ Define how the widget can be resized and keep the same apsect ratio. """
        super().resizeEvent(event)

        if event is None:
            return 
        
        new_size = QtCore.QSize(self.detw, int(self.detw / self.aspect_ratio)) #width, height/(width/height)
        new_size.scale(event.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.resize(new_size)

    def closeEvent(self, event):
        """ 
        Runs when widget is close and ensure the `reader` attribute's 
        `QTimer` is stopped so it can be deleted properly. 
        """
        self.f0.closeEvent(event)
        self.f1.closeEvent(event)
        self.f2.closeEvent(event)
        self.f3.closeEvent(event)
        self.deleteLater()

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
    # reader = CdTeFileReader(datafile)#CdTeReader(data_file_pc)
    # # reader = CdTeReader(datafile)
    
    # f0 = CdTeWidget(data_file_pc=datafile)
    # _f0 =QGridLayout()
    # _f0.addWidget(f0, 0, 0)

    # f1 = CdTeWidget(data_file_pc=datafile)
    # _f1 =QGridLayout()
    # _f1.addWidget(f1, 0, 0)

    # f2 = CdTeWidget(data_file_pc=datafile)
    # _f2 =QGridLayout()
    # _f2.addWidget(f2, 0, 0)

    # f3 = CdTeWidget(data_file_pc=datafile)
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

    cdte0 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte1_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte1_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte1_pc.log")
    cdte1 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte2_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    cdte2 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte3_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte3_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    cdte3 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte4_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte4_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    
    # w.resize(1000,500)
    w = AllCdTeView(cdte0, cdte1, cdte2, cdte3)
    # w = CdTeWidget(data_file_pc=datafile)
    
    w.show()
    app.exec()