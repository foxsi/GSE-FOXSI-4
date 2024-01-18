"""
A demo to walk through an existing CdTe raw file.
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.demos.readRawToRefined_single_cdte import CdTeFileReader
from FoGSE.windows.CdTewindow import CdTeWindow

if __name__=="__main__":
    app = QApplication([])
    
    datafile = os.path.dirname(os.path.realpath(__file__))+"/../data/test_berk_20230728_det05_00007_001"
    # datafile = "/Users/kris/Desktop/cdte_20231025.log"
    reader = CdTeFileReader(datafile)

    f0 = CdTeWindow(reader=reader, plotting_product="spectrogram")
    f0.set_image_colour("green")

    f1 = CdTeWindow(reader=reader, plotting_product="image")
    f1.set_fade_out(5)
    f1.set_image_colour("red")

    f2 = CdTeWindow(reader=reader, plotting_product="image", image_angle=30)
    f2.set_image_colour("red")

    w = QWidget()
    lay = QGridLayout(w)
    lay.addWidget(f0, 1, 0)
    lay.addWidget(f1, 0, 0)
    lay.addWidget(f2, 0, 1)
    w.show()
    app.exec()