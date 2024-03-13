"""
A widget to show off CdTe data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.readers.RTDPlaybackReader import RTDPlaybackReader
from FoGSE.playback.windows.RTDPlaybackWindow import RTDPlaybackWindow
from FoGSE.widgets.RTDWidget import RTDWidget


class RTDPlaybackWidget(RTDWidget):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.RTDReader.RTDReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="RTD", image_angle=0, parent=None):

        RTDWidget.__init__(self, 
                           data_file=data_file, 
                           name=name, 
                           image_angle=image_angle, 
                           parent=parent)

    def get_rtd_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return RTDPlaybackReader
    
    def get_rtd_windows(self):
        """ A way the class can be inherited from but use different parsers. """
        return RTDPlaybackWindow


if __name__=="__main__":
    app = QApplication([])

    DATAFILE = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run19/gse/housekeeping.log"
    
    # w.resize(1000,500)
    w = RTDPlaybackWidget(data_file=DATAFILE)
    # w = QValueWidgetTest()
    w.show()
    app.exec()