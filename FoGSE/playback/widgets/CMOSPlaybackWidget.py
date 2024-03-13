"""
A widget to show off CMOS data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.readers.CMOSPCPlaybackReader import CMOSPCPlaybackReader
from FoGSE.playback.readers.CMOSQLPlaybackReader import CMOSQLPlaybackReader
from FoGSE.playback.readers.CMOSHKPlaybackReader import CMOSHKPlaybackReader
from FoGSE.playback.windows.CMOSPCPlaybackWindow import CMOSPCPlaybackWindow
from FoGSE.playback.windows.CMOSQLPlaybackWindow import CMOSQLPlaybackWindow
from FoGSE.widgets.CMOSWidget import CMOSWidget


class CMOSPlaybackWidget(CMOSWidget):
    """
    An individual window to display CMOS data read from a file.

    Parameters
    ----------
    data_file_pc, data_file_ql : `str`, `str`
        The file to be passed to `FoGSE.readers.CMOSPCPlaybackReader.CMOSPCPlaybackReader()` 
        and `FoGSE.readers.CMOSQLReader.CMOSQLReader()`,
        respectively.
        Default: None

    plotting_product : `str`
        String to determine whether an "image" and or "spectrogram" should be shown.
        Default: "image"
    """
    def __init__(self, data_file_pc=None, data_file_ql=None, data_file_hk=None, name="CMOS", image_angle=0, parent=None):

        CMOSWidget.__init__(self, 
                            data_file_pc=data_file_pc, 
                            data_file_ql=data_file_ql, 
                            data_file_hk=data_file_hk, 
                            name=name, 
                            image_angle=image_angle, 
                            parent=parent)

    def get_cmos_parsers(self):
        """ A way the class can be inherited from but use different parsers. """
        return CMOSPCPlaybackReader, CMOSQLPlaybackReader, CMOSHKPlaybackReader
    
    def get_cmos_windows(self):
        """ A way the class can be inherited from but use different parsers. """
        return CMOSQLPlaybackWindow, CMOSPCPlaybackWindow


if __name__=="__main__":
    app = QApplication([])
    
    
    cmos_pc0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
    cmos_ql0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL
    cmos_pc1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example1/cmos.log"
    cmos_ql1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/cmos_parser/otherExamples-20231102/example2/cmos_ql.log" #QL

    
    cmos_pc0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos1_pc.log"
    cmos_ql0 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos1_ql.log"
    cmos_pc1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos2_pc.log"
    cmos_ql1 = "/Users/kris/Documents/umnPostdoc/projects/both/foxsi4/gse/usingGSECodeForDetAnalysis/feb3/run22/gse/cmos2_ql.log"
    
    # cmos_pc0 = "/Users/kris/Downloads/PC_check_downlink_new.dat"
    # cmos_ql0 = "/Users/kris/Downloads/QL_check_downlink_new.dat"
    # cmos_pc1 = "/Users/kris/Downloads/PC_check_downlink_new.dat"
    # cmos_ql1 = "/Users/kris/Downloads/QL_check_downlink_new.dat"
    
    
    # w.resize(1000,500)
    # w = AllCMOSView(cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1)
    w = CMOSPlaybackWidget(data_file_pc=cmos_pc0, data_file_ql=cmos_ql0, data_file_hk="")
    
    w.show()
    app.exec()