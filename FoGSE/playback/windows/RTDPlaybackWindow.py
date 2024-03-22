"""
A demo to walk through an existing CdTe raw file.
"""

from FoGSE.playback.readers.RTDPlaybackReader import RTDPlaybackReader
from FoGSE.windows.RTDWindow import RTDWindow


class RTDPlaybackWindow(RTDWindow):
    """
    An individual window to display RTD data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.RTDReader.RTDReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.RTDReader.BaseReader()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an \"image\", \"spectrogram\", or \"lightcurve\" 
        should be shown. Only \"lightcurve\"  is supported here.
        Default: \"lightcurve\"
    
    name : `str`
        A useful string that can be used as a label.
        Default: \"RTD\"
    """
    def __init__(self, data_file=None, reader=None, plotting_product="lightcurve", name="RTD", parent=None):

        RTDWindow.__init__(self, data_file=data_file, 
                           reader=reader, 
                           plotting_product=plotting_product, 
                           name=name, 
                           parent=parent)

    def base_essential_get_reader(self):
        """ Return default reader here. """
        return RTDPlaybackReader
    