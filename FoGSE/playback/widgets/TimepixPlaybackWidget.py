"""
A widget to show off CdTe data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.readers.TimepixHKPlaybackReader import TimepixHKPlaybackReader
from FoGSE.playback.readers.TimepixPCAPPlaybackReader import TimepixPCAPPlaybackReader
from FoGSE.playback.windows.TimepixHKPlaybackWindow import TimepixHKPlaybackWindow
from FoGSE.playback.windows.TimepixPCAPPlaybackWindow import TimepixPCAPPlaybackWindow
from FoGSE.widgets.TimepixWidget import TimepixWidget


class TimepixPlaybackWidget(TimepixWidget):
    """
    An individual window to display Timepix data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.TimepixReader.TimepixReader()`.
        Default: None
    """
    def __init__(self, data_file_hk=None, data_file_pcap=None, name="Timepix", image_angle=0, parent=None):

        TimepixWidget.__init__(self, 
                               data_file_hk=data_file_hk, 
                               data_file_pcap=data_file_pcap, 
                               name=name, 
                               image_angle=image_angle, 
                               parent=parent)

    def get_timepix_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return TimepixHKPlaybackReader, TimepixPCAPPlaybackReader
    
    def get_timepix_windows(self):
        """ A way the class can be inherited from but use different parsers. """
        return TimepixHKPlaybackWindow, TimepixPCAPPlaybackWindow


if __name__=="__main__":
    app = QApplication([])

    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame.bin"
    datafile = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/timepix/for_Kris/fake_data_for_parser/example_timepix_frame_writing.bin"
    
    data_file_hk = "/Users/kris/Downloads/timepix_tpx.log"
    data_file_pcap = "/Users/kris/Downloads/timepix_pcap.log"

    # w.resize(1000,500)
    # w = TimepixPlaybackWidget(data_file=datafile)
    # w = QValueWidgetTest()
    w = TimepixPlaybackWidget(data_file_hk=data_file_hk, data_file_pcap=data_file_pcap)
    w.show()
    app.exec()