"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.widgets.CdTeWidget import AllCdTeView
from FoGSE.widgets.CMOSWidget import AllCMOSView
from FoGSE.widgets.TimepixWidget import TimepixWidget

from FoGSE.widgets.layout_tools.spacing import set_all_spacings
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.io.newest_data import newest_data_dir


def get_det_file(want_filename, filename_list):
    """ Returns the filename we're after or an empty string. """
    if want_filename in filename_list:
        return want_filename
    return ""

class GSEDataDisplay(QWidget):
    def __init__(self, parent=None):

        QWidget.__init__(self, parent)

        newest_folder = newest_data_dir() 
        # newest_folder = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run18/gse/"
        newest_folder = "/Users/kris/Downloads/16-2-2024_15-9-8/"
        instruments = [inst for inst in os.listdir(newest_folder) if inst.endswith("log")]

        f0 = AllCdTeView((os.path.join(newest_folder, get_det_file("cdte1_pc.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdte1_hk.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdtede_hk.log", instruments))), 
                        (os.path.join(newest_folder, get_det_file("cdte2_pc.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdte2_hk.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdtede_hk.log", instruments))), 
                        (os.path.join(newest_folder, get_det_file("cdte3_pc.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdte3_hk.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdtede_hk.log", instruments))), 
                        (os.path.join(newest_folder, get_det_file("cdte4_pc.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdte4_hk.log", instruments)), 
                          os.path.join(newest_folder, get_det_file("cdtede_hk.log", instruments))))
        # f0 = AllCdTeView(os.path.join(newest_folder, get_det_file("cdte1.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte2.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte3.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte4.log", instruments)))
        # newest_folder = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run21/gse/"
        f1 = AllCMOSView(os.path.join(newest_folder, get_det_file("cmos1_pc.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos1_ql.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos2_pc.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos2_ql.log", instruments)), 
                        cmos_hk0=os.path.join(newest_folder, get_det_file("cmos1_hk.log", instruments)), 
                        cmos_hk1=os.path.join(newest_folder, get_det_file("cmos2_hk.log", instruments)))
        
        f2 = TimepixWidget(os.path.join(newest_folder, get_det_file("timepix_tpx.log", instruments)))
        # f2 = TimepixWidget("/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin")

        lay = QGridLayout()

        lay.addWidget(f0, 0, 0, 3, 12)
        lay.addWidget(f1, 3, 0, 3, 12)
        lay.addWidget(f2, 6, 0, 2, 4)
        
        # w.resize(1000,500)
        # _s = 122
        # w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        set_all_spacings(lay)
        unifrom_layout_stretch(lay, grid=True)

        self.setLayout(lay)

if __name__=="__main__":
    app = QApplication([])

    w = GSEDataDisplay()

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()
    
    app.exec()