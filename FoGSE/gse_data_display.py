"""
First go at a full GSE (data viewing only).
"""
import os
import sys

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

from FoGSE.widgets.CdTeWidgetGroup import AllCdTeView
from FoGSE.widgets.CMOSWidgetGroup import AllCMOSView
from FoGSE.widgets.TimepixWidget import TimepixWidget
from FoGSE.widgets.CatchWidget import CatchWidget
from FoGSE.widgets.DisplayCommandWidget import DisplayCommandWidget

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

        newest_folder = self.get_data_dir() 
        # newest_folder = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run14/gse/"
        # newest_folder = "/Users/kris/Downloads/16-2-2024_15-9-8/"
        instruments = [inst for inst in os.listdir(newest_folder) if inst.endswith("log")]

        cdte_view, cmos_view, timepix_view, disp_comm_view, catch_view = self.get_all_detector_views()

        self.f0 = cdte_view((os.path.join(newest_folder, get_det_file("cdte1_pc.log", instruments)), 
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
        # f0 = cdte_view(os.path.join(newest_folder, get_det_file("cdte1.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte2.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte3.log", instruments)), 
        #                  os.path.join(newest_folder, get_det_file("cdte4.log", instruments)))
        # newest_folder = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run21/gse/"
        self.f1 = cmos_view(os.path.join(newest_folder, get_det_file("cmos1_pc.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos1_ql.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos2_pc.log", instruments)), 
                        os.path.join(newest_folder, get_det_file("cmos2_ql.log", instruments)), 
                        cmos_hk0=os.path.join(newest_folder, get_det_file("cmos1_hk.log", instruments)), #"/Users/kris/Downloads/cmos1_hk.log",#
                        cmos_hk1=os.path.join(newest_folder, get_det_file("cmos2_hk.log", instruments)))
        
        self.f2 = timepix_view(os.path.join(newest_folder, get_det_file("timepix_tpx.log", instruments)))
        # f2 = timepix_view("/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin")

        self.f3 = disp_comm_view()
        self.f3.rotation_slider.valueChanged.connect(self.propagate_rotation)
        self.f3.default_rotation_button.clicked.connect(self.default_rotation)
        self.f3.clear_image_button.clicked.connect(self.clear_images)

        self.f4 = catch_view(data_file=os.path.join(newest_folder, get_det_file("catch.log", instruments)))
        

        lay = QGridLayout()

        lay.addWidget(self.f0, 0, 0, 3, 12)
        lay.addWidget(self.f1, 3, 0, 3, 12)
        lay.addWidget(self.f2, 6, 0, 2, 4)
        lay.addWidget(self.f3, 6, 4, 2, 4)
        lay.addWidget(self.f4, 6, 8, 2, 4)
        
        # w.resize(1000,500)
        # _s = 122
        # w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
        # w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

        set_all_spacings(lay, s=1)
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

    def get_all_detector_views(self):
        """ A way the class can be inherited from but use different views. """
        return AllCdTeView, AllCMOSView, TimepixWidget, DisplayCommandWidget, CatchWidget
    
    def get_data_dir(self):
        """ A way the class can be inherited from but use different folders. """
        return newest_data_dir() 
    
    def propagate_rotation(self):
        """ Apply the rotation displayed on the slider to the image windows. """
        if not hasattr(self, "cdte1_rot_default"): self.cdte1_rot_default = self.f0.f0.image.image_angle
        if not hasattr(self, "cdte2_rot_default"): self.cdte2_rot_default = self.f0.f1.image.image_angle
        if not hasattr(self, "cdte3_rot_default"): self.cdte3_rot_default = self.f0.f2.image.image_angle
        if not hasattr(self, "cdte4_rot_default"): self.cdte4_rot_default = self.f0.f3.image.image_angle
        if not hasattr(self, "cmos1_rot_default"): self.cmos1_rot_default = self.f1.f0.ql.image_angle
        if not hasattr(self, "cmos2_rot_default"): self.cmos2_rot_default = self.f1.f1.ql.image_angle
        rotation = self.f3.rotation_slider.value()
        self.f0.f0.image.update_rotation(self.cdte1_rot_default+rotation)
        self.f0.f1.image.update_rotation(self.cdte2_rot_default+rotation)
        self.f0.f2.image.update_rotation(self.cdte3_rot_default+rotation)
        self.f0.f3.image.update_rotation(self.cdte4_rot_default+rotation)
        self.f1.f0.ql.update_rotation(self.cmos1_rot_default+rotation)
        self.f1.f1.ql.update_rotation(self.cmos2_rot_default+rotation)

    def default_rotation(self):
        """ Reset the rotation of th windows to their defaults. """
        self.f3.rotation_slider.setValue(0)

    def clear_images(self):
        """ Clear the display images to start integation again. """
        self.f0.f0.image.base_clear_image()
        self.f0.f0.ped.base_clear_image()

        self.f0.f1.image.base_clear_image()
        self.f0.f1.ped.base_clear_image()

        self.f0.f2.image.base_clear_image()
        self.f0.f2.ped.base_clear_image()

        self.f0.f3.image.base_clear_image()
        self.f0.f3.ped.base_clear_image()

        self.f1.f0.ql.base_clear_image()
        self.f1.f0.pc.base_clear_image()

        self.f1.f1.ql.base_clear_image()
        self.f1.f1.pc.base_clear_image()

    def check_current_window(self):
        """ 
        Method to alert the user if this widget is not the active window.
        
        On Mac at least, this will bounce the icon in the dock to show
        the window isn't active. Of course this helps when the window has 
        to be active for Tooltops and other things relying on QEvents to 
        work.
        """
        self.app.alert(self,0)
        self.app.processEvents()

    def closeEvent(self, event):
        """ 
        Runs when widget is close and ensure the `reader` attribute's 
        `QTimer` is stopped so it can be deleted properly. 
        """
        # self.f0.closeEvent(event)
        # self.f1.closeEvent(event)
        # self.f2.closeEvent(event)
        # self.f3.closeEvent(event)
        # self.f4.closeEvent(event)
        # self.deleteLater()
        sys.exit()

if __name__=="__main__":
    import time
    app = QApplication([])

    w = GSEDataDisplay(window_alert=True)

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()
    
    app.exec()