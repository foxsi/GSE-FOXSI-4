"""
A widget to show off CdTe data.
"""

from FoGSE.playback.readers.CatchPlaybackReader import CatchPlaybackReader
from FoGSE.widgets.CatchWidget import CatchWidget

class CatchPlaybackWidget(CatchWidget):
    """
    An individual window to display Power data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.PowerReader.PowerReader()`.
        Default: None
    """
    def __init__(self, data_file=None, name="Catch", parent=None):

        CatchWidget.__init__(self, data_file=data_file, name=name, parent=parent)

    def get_catch_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return CatchPlaybackReader
    
    