"""
First go at a full GSE (data viewing only).
"""
import os

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.widgets.CdTeWidget import AllCdTeView
from FoGSE.widgets.CMOSWidget import AllCMOSView
from FoGSE.widgets.TimepixWidget import TimepixWidget
from FoGSE.widgets.RTDWidget import RTDWidget
from FoGSE.widgets.PowerWidget import PowerWidget

from FoGSE.widgets.layout_tools.spacing import set_all_spacings
from FoGSE.widgets.layout_tools.stretch import unifrom_layout_stretch
from FoGSE.io.newest_data import newest_data_dir


def get_det_file(want_filename, filename_list):
    """ Returns the filename we're after or an empty string. """
    if want_filename in filename_list:
        return want_filename
    return ""

class GSEDataDisplay(QWidget):
    def __init__(self, window_alert=False, parent=None):

        QWidget.__init__(self, parent)

        newest_folder = newest_data_dir() 
        # newest_folder = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run14/gse/"
        # newest_folder = "/Users/kris/Downloads/16-2-2024_15-9-8/"
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
                        cmos_hk0=os.path.join(newest_folder, get_det_file("cmos1_hk.log", instruments)), #"/Users/kris/Downloads/cmos1_hk.log",#
                        cmos_hk1=os.path.join(newest_folder, get_det_file("cmos2_hk.log", instruments)))
        
        f2 = TimepixWidget(os.path.join(newest_folder, get_det_file("timepix_tpx.log", instruments)))
        # f2 = TimepixWidget("/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin")

        f3 = RTDWidget(os.path.join(newest_folder, get_det_file("housekeeping_rtd.log", instruments)))

        f4 = PowerWidget(os.path.join(newest_folder, get_det_file("housekeeping_pow.log", instruments)))
        # f4 = PowerWidget("/Users/kris/Downloads/housekeeping_pow.log")

        lay = QGridLayout()

        lay.addWidget(f0, 0, 0, 3, 12)
        lay.addWidget(f1, 3, 0, 3, 12)
        lay.addWidget(f2, 6, 0, 2, 4)
        lay.addWidget(f3, 6, 4, 2, 4)
        lay.addWidget(f4, 6, 7, 2, 5)
        
        # w.resize(1000,500)
        # _s = 122
        # w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        set_all_spacings(lay)
        unifrom_layout_stretch(lay, grid=True)

        self.setLayout(lay)
        
        # get the currect application
        self.app = QApplication.instance()
        # if signals are sent before everything starts up properly they can get stuck
        # Need to process the pending events and this seems to fix things
        # https://doc.qt.io/qtforpython-5/PySide2/QtCore/QCoreApplication.html#PySide2.QtCore.PySide2.QtCore.QCoreApplication.processEvents
        self.app.processEvents()

        if window_alert:
            self.timer = QtCore.QTimer()
            # having 0 should work but appears to be intermittent
            # ~2 seconds seems to be the period of the Mac bounce animation
            self.timer.setInterval(2000) 
            self.timer.timeout.connect(self.check_current_window) # call self.update_plot_data every cycle
            self.timer.start()

    def check_current_window(self):
        """ 
        Method to alert the user if this widget is not the active window.
        
        On Mac at least, this will bounce the icon in the dock to show
        the window isn't active. Of course this helps when the window has 
        to be active for Tooltops and other things relying on QEvents to 
        work.
        """
        self.app.alert(self,0)

if __name__=="__main__":
    import time
    app = QApplication([])
    icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'FOXSI4_32.png')
    print(icon_path)
    app.setWindowIcon(QtGui.QIcon(icon_path))
    w = GSEDataDisplay(window_alert=True)

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()
    
    app.exec()