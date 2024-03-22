import sys, typing, logging
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QStyleFactory, QTabWidget, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon

from FoGSE.visualization import DetectorArrayDisplay, DetectorGridDisplay, DetectorPlotView, GlobalCommandPanel, PowerMonitorView
from FoGSE.communication import FormatterUDPInterface
from FoGSE.configuration import SystemConfiguration, SettingsPanel
from FoGSE.widgets.CommandUplinkWidget import CommandUplinkWidget

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

ORG_NAME = "FOXSI"
APP_NAME = "GSE-FOXSI-4"

class GSEMain(QMainWindow):
    def __init__(self):
        super().__init__()                              # init the superclass

        # setup the window: -----------------------------------------------------
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        QApplication.setStyle(QStyleFactory.create("macOS"))
        # can check available styles with:
        # print(QStyleFactory.keys())

        # self.settings = self._restoreSettings()         # restore old settings

        # SystemConfiguration should instantiate FormatterUDPInterface?

        self.fmtrif = FormatterUDPInterface(logging=True, logfilename=None)
        self.config = SystemConfiguration(formatter_if=self.fmtrif)
        
        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)
        # self.setCentralWidget(DetectorArrayDisplay(self))
        # self.setCentralWidget(DetectorGridDisplay(self, configuration=self.config, formatter_if=self.fmtrif))
        self.setCentralWidget(SettingsPanel(self))
        # self.setCentralWidget(DetectorPlotView(self))
        
        # logging.debug(str(self.width()) + str(self.height()))

        # setup app-wide attributes: --------------------------------------------
        self.uplinkCommandCount = 0
        
        # self.fmtrif.listen_thread.start()

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

        self.setCentralWidget(DetectorPlotView(self))

        
        
class GSECommand(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        # self.settings = self._restoreSettings()         # restore old settings

        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)

        self.fmtrif = FormatterUDPInterface(logging=True, logfilename=None)
        self.config = SystemConfiguration(formatter_if=self.fmtrif)

        self.setCentralWidget(CommandUplinkWidget(self, name="Command", configuration=self.config, formatter_if=self.fmtrif))
        # self.setCentralWidget(PowerMonitorView(self, configuration=self.config, formatter_if=self.fmtrif))