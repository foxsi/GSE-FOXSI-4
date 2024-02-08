"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.widgets.CdTeWidget import AllCdTeView
from FoGSE.widgets.CMOSWidget import AllCMOSView

from FoGSE.widgets.layout_tools.spacing import set_all_spacings
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.io.newest_data import newest_data_dir

# from FoGSE.visualization import GlobalCommandPanel


def get_det_file(want_filename, filename_list):
    """ Returns the filename we're after or an empty string. """
    if want_filename in filename_list:
        return want_filename
    return ""

if __name__=="__main__":
    app = QApplication([])

    # newest_folder = newest_data_dir() 
    # # newest_folder = "/Users/kris/Downloads/jan30/run17/gse"
    # cdte_instruments = [inst for inst in os.listdir(newest_folder) if inst.endswith("log")]
    
    f0 = AllCdTeView("/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cdte1.log",
                     "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cdte2.log",
                     "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cdte3.log",
                     "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cdte4.log")

    f1 = AllCMOSView("/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cmos1_pc.log",
                 "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cmos1_ql.log",
                 "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cmos2_pc.log",
                 "/Users/foxsi/Documents/FOXSI/foxsi-4matter/log/gse/cmos2_ql.log")

    w = QWidget()
    lay = QGridLayout(w)

    lay.addWidget(f0, 0, 0, 1, 1)
    lay.addWidget(f1, 1, 0, 1, 1)
    
    # w.resize(1000,500)
    w.setGeometry(100,100,2000, 870)
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    set_all_spacings(lay)
    unifrom_layout_stretch(lay, grid=True)

    w.show()

    # x = QWidget()
    # lay = QGridLayout(x)
    # glc = GlobalCommandPanel()
    # lay.addWidget(glc, 0, 0, 1, 1)
    # x.show()
    
    app.exec()