"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.read_raw_to_refined.readRawToRefinedCdTe import CdTeReader
from FoGSE.demos.readRawToRefined_single_cdte import CdTeFileReader
from FoGSE.read_raw_to_refined.readRawToRefinedCMOS import CMOSPCReader
from FoGSE.read_raw_to_refined.readRawToRefinedCMOSQL import CMOSQLReader

from FoGSE.windows.CdTeWindow import CdTeWindow
from FoGSE.windows.CMOSPCWindow import CMOSPCWindow
from FoGSE.windows.CMOSQLWindow import CMOSQLWindow

if __name__=="__main__":
    app = QApplication([])
    
    datafile0 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    datafile1 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    datafile2 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    datafile3 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    datafile4 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log" #PC
    datafile5 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL
    datafile6 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" # "TIMEPIX"

    reader0 = CdTeFileReader(datafile0)
    reader1 = CdTeFileReader(datafile1)
    reader2 = CdTeFileReader(datafile2)
    reader3 = CdTeFileReader(datafile3)
    reader4 = CMOSPCReader(datafile4)
    reader5 = CMOSPCReader(datafile5)
    reader6 = CMOSQLReader(datafile6)

    f0 = CdTeWindow(reader=reader0, plotting_product="image")
    f0.set_image_colour("green")
    f0.update_background(colour=(80,40,10,100))

    f1 = CdTeWindow(reader=reader1, plotting_product="image")
    f1.set_fade_out(5)
    f1.set_image_colour("red")

    f2 = CdTeWindow(reader=reader2, plotting_product="image", image_angle=30)
    f2.set_image_colour("blue")

    f3 = CdTeWindow(reader=reader3, plotting_product="image", image_angle=45)
    f3.set_image_colour("green")

    f4 = CMOSPCWindow(reader=reader4, plotting_product="image")

    f5 = CMOSPCWindow(reader=reader5, plotting_product="image", image_angle=-15)
    f5.set_image_colour("blue")

    f6 = CMOSQLWindow(reader=reader6, plotting_product="image", image_angle=10)
    f6.set_image_colour("red")# TIMEPIX

    w = QWidget()
    lay = QGridLayout(w)

    lay.addWidget(f0, 0, 0, 1, 2)
    lay.addWidget(f1, 0, 2, 1, 2)
    lay.addWidget(f2, 0, 4, 1, 2)
    lay.addWidget(f3, 0, 6, 1, 2)
    lay.addWidget(f4, 1, 0, 1, 4)
    lay.addWidget(f5, 1, 4, 1, 4)
    lay.addWidget(f6, 3, 0, 1, 3)
    
    w.resize(1000,500)
    w.show()
    app.exec()