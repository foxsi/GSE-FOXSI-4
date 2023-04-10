import sys, typing, logging
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QStyleFactory
from PyQt6.QtGui import QIcon

from FoGSE.visualization import DetectorArrayDisplay, DetectorGridDisplay, DetectorPanel, GlobalCommandPanel
from FoGSE.communication import FormatterUDPInterface

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

ORG_NAME = "FOXSI"
APP_NAME = "GSE-FOXSI-4"

class GSEMain(QMainWindow):
    def __init__(self):
        super().__init__()                              # init the parent

        # setup the window: -----------------------------------------------------
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        QApplication.setStyle(QStyleFactory.create("macOS"))
        # can check available styles with:
        # print(QStyleFactory.keys())

        # self.settings = self._restoreSettings()         # restore old settings

        fmtrif = FormatterUDPInterface(addr="127.0.0.1", port=9999, logging=True, logfilename=None)
        
        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)
        # self.setCentralWidget(DetectorArrayDisplay(self))
        self.setCentralWidget(DetectorGridDisplay(self, fmtrif))
        # self.setCentralWidget(DetectorPanel(self))
        
        # logging.debug(str(self.width()) + str(self.height()))

        # setup app-wide attributes: --------------------------------------------
        self.uplinkCommandCount = 0
        

    def _restoreSettings(self):
        settings = QSettings(ORG_NAME,APP_NAME)
        # settings.beginGroup("GSEMain")  # or whatever the main window's top-level settings group is called
        # someSetting = settings.value("<some setting key>", QByteArray()).toByteArray()
        # if someSetting.isEmpty():
        #     return default

class GSEFocus(QMainWindow):
    def __init__(self):
        super().__init__()                              # init the parent
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        # self.settings = self._restoreSettings()         # restore old settings
        
        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)

        self.setCentralWidget(DetectorPanel(self))
        
class GSECommand(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        # self.settings = self._restoreSettings()         # restore old settings

        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)

        fmtrif = FormatterUDPInterface(addr="127.0.0.1", port=9999, logging=True, logfilename=None)

        self.setCentralWidget(GlobalCommandPanel(self, fmtrif))