"""
First go at a full GSE (data viewing only).
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.widgets.CdTePlaybackWidgetGroup import AllPlaybackCdTeView
from FoGSE.playback.widgets.CMOSPlaybackWidgetGroup import AllPlaybackCMOSView
from FoGSE.playback.widgets.TimepixPlaybackWidget import TimepixPlaybackWidget
from FoGSE.playback.widgets.DisplayCommandPlaybackWidget import DisplayCommandWidget

from FoGSE.io.newest_data import newest_data_dir

from FoGSE.gse_data_display import GSEDataDisplay


class GSEPlaybackDataDisplay(GSEDataDisplay):
    def __init__(self, window_alert=False, parent=None):

        GSEDataDisplay.__init__(self, window_alert=window_alert, parent=parent)

    def get_all_detector_views(self):
        """ A way the class can be inherited from but use different views. """
        return AllPlaybackCdTeView, AllPlaybackCMOSView, TimepixPlaybackWidget, DisplayCommandWidget
    
    def get_data_dir(self):
        """ A way the class can be inherited from but use different folders. """
        # return newest_data_dir() 
        return "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/"

if __name__=="__main__":
    import time
    app = QApplication([])

    w = GSEPlaybackDataDisplay(window_alert=True)

    _s = 122
    w.setGeometry(0,0, 12*_s, 8*_s) # 12 to 8
    w.setStyleSheet("border-width: 2px; border-style: outset; border-radius: 10px; border-color: white; background-color: rgba(238, 186, 125, 150);")

    w.show()
    
    app.exec()