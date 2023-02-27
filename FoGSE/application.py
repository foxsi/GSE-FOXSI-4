import sys, typing, logging
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

from FoGSE.visualization import DetectorArrayDisplay, DetectorPanel

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

ORG_NAME = "FOXSI"
APP_NAME = "GSE-FOXSI-4"

class GSEMain(QMainWindow):
    def __init__(self):
        super().__init__()                              # init the parent
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        # self.settings = self._restoreSettings()         # restore old settings
        
        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)

        # self.widgets = DetectorPanel()                  # add widgets to display
        logging.debug(str(self.width()) + str(self.height()))
        self.setCentralWidget(DetectorArrayDisplay(self))
        # self.setCentralWidget(DetectorPanel(self))
        logging.debug(str(self.width()) + str(self.height()))
        
        # spawn threads

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

        logging.debug(self.width(), self.height())
        self.setCentralWidget(DetectorPanel(self))
        logging.debug(self.width(), self.height())
        