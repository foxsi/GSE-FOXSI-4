"""
A demo to walk through an existing CdTe raw file.
"""

from FoGSE.playback.readers.CdTePCPlaybackReader import CdTePCPlaybackReader
from FoGSE.windows.CdTeWindow import CdTeWindow


class CdTePlaybackWindow(CdTeWindow):
    """
    An individual window to display CdTe data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.CdTePCReader.CdTePCReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.CdTePCReader.BaseReader()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an "image", "spectrogram", or "lightcurve" 
        should be shown.
        Default: \"image\"

    image_angle : `int`, `float`, etc.
        The angle of roation for the plot. Positive is anti-clockwise and 
        negative is clockwise.
        Default: 0
    
    update_method : `str`
        Indicates whether the frames (if that is relevant `plotting_product`)
        should be summed continously, unless told otherwise.
        Default: \"integrate\"
    
    name : `str`
        A useful string that can be used as a label.
        Default: \"CdTe\"
        
    colour : `str`
        The colour channel used, if used for the `plotting_product`. 
        Likely from [\"red\", \"green\", \"blue\"].
        Default: \"green\"
    """

    def __init__(self, data_file=None, reader=None, plotting_product="image", image_angle=0, update_method="integrate", name="CdTe", colour="green", colour_twin="red", parent=None):

        CdTeWindow.__init__(self, 
                            data_file=data_file, 
                            reader=reader, 
                            plotting_product=plotting_product, 
                            image_angle=image_angle, 
                            update_method=update_method, 
                            name=name, 
                            colour=colour, 
                            colour_twin=colour_twin,
                            parent=parent)

    def base_essential_get_reader(self):
        """ Return default reader here. """
        return CdTePCPlaybackReader
    