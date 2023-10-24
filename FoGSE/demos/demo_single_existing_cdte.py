"""
A demo to walk through an existing CdTe raw file.
"""
import os

from PyQt6.QtWidgets import QApplication

from FoGSE.demos.readRawToRefined_single_cdte import CdTeFileReader
from FoGSE.windows.windowCdTe import WindowCdTe

if __name__=="__main__":
    app = QApplication([])
    
    datafile = os.path.dirname(os.path.realpath(__file__))+"/../data/test_berk_20230728_det05_00007_001"
    reader = CdTeFileReader(datafile)

    f0 = WindowCdTe(reader=reader, plotting_product="spectrogram")
    f0.set_image_colour("green")

    f1 = WindowCdTe(reader=reader, plotting_product="image")
    f1.set_fade_out(5)
    f1.set_image_colour("red")

    f0.show()
    f1.show()
    app.exec()