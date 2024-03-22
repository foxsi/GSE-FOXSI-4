"""
A demo to walk through a CMOS QL raw file.
"""

from FoGSE.playback.readers.CMOSQLPlaybackReader import CMOSQLPlaybackReader
from FoGSE.windows.CMOSQLWindow import CMOSQLWindow


class CMOSQLPlaybackWindow(CMOSQLWindow):
    """
    An individual window to display CMOS data read from a file.

    Parameters
    ----------
    data_file : `str` 
        The file to be passed to `FoGSE.readers.CMOSQLReader.CMOSQLReader()`.
        If given, takes priority over `reader` input.
        Default: None

    reader : instance of `FoGSE.readers.CMOSQLReader.BaseReader()`
        The reader already given a file.
        Default: None

    plotting_product : `str`
        String to determine whether an "image" and or <something else> should be shown.
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
        Default: \"CMOS\"
        
    colour : `str`
        The colour channel used, if used for the `plotting_product`. 
        Likely from [\"red\", \"green\", \"blue\"].
        Default: \"green\"
    """

    def __init__(self, data_file=None, reader=None, plotting_product="image", image_angle=0, update_method="integrate", name="CMOS", colour="green", parent=None, ave_background_frame=0):
        
        CMOSQLWindow.__init__(self, 
                              data_file=data_file, 
                              reader=reader, 
                              plotting_product=plotting_product, 
                              image_angle=image_angle, 
                              update_method=update_method, 
                              name=name, 
                              colour=colour, 
                              parent=parent,
                              ave_background_frame=ave_background_frame)
    
    def base_essential_get_reader(self):
        """ Return default reader here. """
        return CMOSQLPlaybackReader
    