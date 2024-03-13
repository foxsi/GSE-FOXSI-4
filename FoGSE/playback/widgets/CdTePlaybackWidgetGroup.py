"""
A widget to show off CdTe data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.widgets.CdTePlaybackWidget import CdTePlaybackWidget
from FoGSE.widgets.CdTeWidgetGroup import AllCdTeView


class AllPlaybackCdTeView(AllCdTeView):
    def __init__(self, cdte0, cdte1, cdte2, cdte3):
        AllCdTeView.__init__(self, cdte0, cdte1, cdte2, cdte3)     

    def get_cdte_widget(self):
        """ A way the class can be inherited from but use different parsers. """
        return CdTePlaybackWidget

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
    cdte1 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte2_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte2_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    cdte2 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte3_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte3_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    cdte3 = ("/Users/kris/Downloads/16-2-2024_15-9-8/cdte4_pc.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdte4_hk.log", 
             "/Users/kris/Downloads/16-2-2024_15-9-8/cdtede_hk.log")
    
    # w.resize(1000,500)
    w = AllPlaybackCdTeView(cdte0, cdte1, cdte2, cdte3)
    # w = CdTeWidget(data_file_pc=datafile)
    
    w.show()
    app.exec()