"""
A widget to show off CMOS data.
"""
from PyQt6.QtWidgets import QApplication

from FoGSE.playback.widgets.CMOSPlaybackWidget import CMOSPlaybackWidget
from FoGSE.widgets.CMOSWidgetGroup import AllCMOSView


class AllPlaybackCMOSView(AllCMOSView):
    def __init__(self, cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1, cmos_hk0=None, cmos_hk1=None):
        AllCMOSView.__init__(self, cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1, cmos_hk0=cmos_hk0, cmos_hk1=cmos_hk1)     

    def get_cmos_widget(self):
        """ A way the class can be inherited from but use different parsers. """
        return CMOSPlaybackWidget


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
    
    cmos_pc0 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos1_pc.log"
    cmos_ql0 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos1_ql.log"
    cmos_hk0 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos1_hk.log"
    cmos_pc1 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos2_pc.log"
    cmos_ql1 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos2_ql.log"
    cmos_hk1 = "/Users/kris/Downloads/feb17_no_cmos/run22/17-2-2024_21-2-23/cmos2_hk.log"
    
    
    # w.resize(1000,500)
    w = AllPlaybackCMOSView(cmos_pc0, cmos_ql0, cmos_pc1, cmos_ql1, cmos_hk0=cmos_hk0, cmos_hk1=cmos_hk1)
    # w = CMOSWidget(data_file_pc=data_file_pc, data_file_ql=data_file_ql)
    
    w.show()
    app.exec()