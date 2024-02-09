"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.gse_data_display import GSEDataDisplay

from FoGSE.visualization import GlobalCommandPanel


def get_det_file(want_filename, filename_list):
    """ Returns the filename we're after or an empty string. """
    if want_filename in filename_list:
        return want_filename
    return ""

if __name__=="__main__":
    app = QApplication([])

    w = GSEDataDisplay()

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()

    x = QWidget()
    lay = QGridLayout(x)
    glc = GlobalCommandPanel()
    lay.addWidget(glc, 0, 0, 1, 1)
    x.show()
    
    app.exec()