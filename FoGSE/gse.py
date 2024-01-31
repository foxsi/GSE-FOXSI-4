"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

# from FoGSE.read_raw_to_refined.readRawToRefinedCdTe import CdTeReader
# from FoGSE.demos.readRawToRefined_single_cdte import CdTeFileReader
# from FoGSE.read_raw_to_refined.readRawToRefinedCMOS import CMOSPCReader
# from FoGSE.read_raw_to_refined.readRawToRefinedCMOSQL import CMOSQLReader

from FoGSE.widgets.CdTeWidget import AllCdTeView
from FoGSE.widgets.CMOSWidget import AllCMOSView

from FoGSE.widgets.layout_tools.spacing import set_all_spacings
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch

if __name__=="__main__":
    app = QApplication([])
    
    # datafile0 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    # datafile1 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    # datafile2 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    # datafile3 = os.path.dirname(os.path.realpath(__file__))+"/data/test_berk_20230728_det05_00007_001"
    # datafile4 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log" #PC
    # datafile5 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL
    # datafile6 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" # "TIMEPIX"

    # reader0 = CdTeFileReader(datafile0)
    # reader1 = CdTeFileReader(datafile1)
    # reader2 = CdTeFileReader(datafile2)
    # reader3 = CdTeFileReader(datafile3)
    # reader4 = CMOSPCReader(datafile4)
    # reader5 = CMOSPCReader(datafile5)
    # reader6 = CMOSQLReader(datafile6)

    f0 = AllCdTeView()

    f1 = AllCMOSView()

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
    app.exec()