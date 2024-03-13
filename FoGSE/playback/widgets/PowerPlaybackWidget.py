"""
A widget to show off CdTe data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.readers.PowerPlaybackReader import PowerPlaybackReader
from FoGSE.widgets.PowerWidget import PowerWidget

class PowerPlaybackWidget(PowerWidget):
    """
    An individual window to display Power data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.PowerReader.PowerReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="Power", image_angle=0, parent=None):

        PowerWidget.__init__(self, 
                             data_file=data_file, 
                             name=name, 
                             image_angle=image_angle, 
                             parent=parent)

    def get_power_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return PowerPlaybackReader
    

if __name__=="__main__":
    app = QApplication([])

    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"
    
    # w.resize(1000,500)
    w = PowerPlaybackWidget(data_file=datafile)
    # w = QValueWidgetTest()
    w.show()
    app.exec()