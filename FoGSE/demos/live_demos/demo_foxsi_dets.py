"""
A demo to walk through an existing CdTe raw file.
"""
import os
import sys

from PyQt6.QtWidgets import QApplication

from FoGSE.readers.CdTePCReader import CdTeReader
from FoGSE.readres.CMOSPCReader import CMOSPCReader
from FoGSE.readers.CMOSQLReader import CMOSQLReader
from FoGSE.readers.RTDReader import RTDReader
from FoGSE.windows.CdTeWindow import CdTeWindow
from FoGSE.windows.CMOSPCWindow import CMOSPCWindow
from FoGSE.windows.CMOSQLWindow import CMOSQLWindow
from FoGSE.windows.RTDWindow import RTDWindow

def run_windows(*args):
    """ Opens up user given windows for FOXSI instruments. """
    app = QApplication([])
    
    # `datafile = os.path.dirname(os.path.realpath(__file__))+"/../data/test_berk_20230728_det05_00007_001"`
    det_list = ["cdte_ped", "cdte_im", "cmos_pc", "cmos_ql", "rtd"]

    # det_args = sys.argv[1:]
    if len(args)%2!=0:
        print("Need `python <det1> <file1> <det2> <file2>` and so on.")
        exit()

    dets = args[::2]
    det_files = args[1::2]

    windows = []
    for d,f in zip(dets, det_files):

        if d not in det_list:
            print(f"{d} not in list. Dets are {det_list}")
            continue

        # ensure we get a pure path+file, no Windows nonesense
        drive, path_and_file = os.path.splitdrive(f) 
        path, file = os.path.split(path_and_file)

        if d=="cdte_ped":
            window = CdTeWindow(reader=CdTeReader(f), plotting_product="spectrogram", name=file)
        elif d=="cdte_im":
            window = CdTeWindow(reader=CdTeReader(f), plotting_product="image", name=file)
        elif d=="cmos_pc":
            window = CMOSPCWindow(reader=CMOSPCReader(f), plotting_product="image", name=file)
        elif d=="cmos_ql":
            window = CMOSQLWindow(reader=CMOSQLReader(f), plotting_product="image", name=file)
        elif d=="rtd":
            window = RTDWindow(reader=RTDReader(f), name=file)

        windows.append(window)

    for w in windows:
        w.show()

    app.exec()

if __name__=="__main__":
    run_windows(*sys.argv[1:])
    # app = QApplication([])
    
    # # `datafile = os.path.dirname(os.path.realpath(__file__))+"/../data/test_berk_20230728_det05_00007_001"`
    # det_list = ["cdte_ped", "cdte_im", "cmos_pc", "cmos_ql", "rtd"]

    # det_args = sys.argv[1:]
    # if len(det_args)%2!=0:
    #     print("Need `python <det1> <file1> <det2> <file2>` and so on.")
    #     exit()

    # dets = det_args[::2]
    # det_files = det_args[1::2]

    # windows = []
    # for d,f in zip(dets, det_files):

    #     if d not in det_list:
    #         print(f"{d} not in list. Dets are {det_list}")
    #         continue

    #     # ensure we get a pure path+file, no Windows nonesense
    #     drive, path_and_file = os.path.splitdrive(f) 
    #     path, file = os.path.split(path_and_file)

    #     if d=="cdte_ped":
    #         window = CdTeWindow(reader=CdTeReader(f), plotting_product="spectrogram", name=file)
    #     elif d=="cdte_im":
    #         window = CdTeWindow(reader=CdTeReader(f), plotting_product="image", name=file)
    #     elif d=="cmos_pc":
    #         window = CMOSWindow(reader=CMOSReader(f), plotting_product="image", name=file)
    #     elif d=="cmos_ql":
    #         window = QLCMOSWindow(reader=QLCMOSReader(f), plotting_product="image", name=file)
    #     elif d=="rtd":
    #         window = RTDWindow(reader=RTDReader(f), name=file)

    #     windows.append(window)

    # for w in windows:
    #     w.show()

    # app.exec()