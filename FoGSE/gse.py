"""
First go at a full GSE (data viewing only).
"""
import os
from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout

from FoGSE.gse_data_display import GSEDataDisplay

from FoGSE.widgets.CommandUplinkWidget import CommandUplinkWidget


def get_det_file(want_filename, filename_list):
    """ Returns the filename we're after or an empty string. """
    if want_filename in filename_list:
        return want_filename
    return ""

if __name__=="__main__":
    app = QApplication([])
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'FOXSI4_32.png')
    app.setWindowIcon(QtGui.QIcon(icon_path))
    
    x = QWidget()
    lay = QVBoxLayout(x)
    glc = CommandUplinkWidget()
    lay.addWidget(glc)
    x.show()

    w = GSEDataDisplay()

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()

    
    app.exec()