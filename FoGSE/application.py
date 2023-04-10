import sys, typing, logging
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QStyleFactory, QTabWidget, QWidget, QHBoxLayout
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

        self.fmtrif = FormatterUDPInterface(addr="127.0.0.1", port=9999, logging=True, logfilename=None)
        
        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)
        # self.setCentralWidget(DetectorArrayDisplay(self))
        self.setCentralWidget(DetectorGridDisplay(self, self.fmtrif))
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



class GSEPopout(QWidget):
    def __init__(self, detector_panel: DetectorPanel):
        super().__init__()                              # init the parent

        # keep a pointer to the main display to reparent popout to on close
        self.detector_panel = detector_panel
        self.grid_display = self.detector_panel.parent()

        # remove the detector_panel from its original grid_display
        self.grid_display.grid_layout.removeWidget(self.detector_panel)

        # find detector_panel in grid_display.gridLayout (to put it back later)
        self._restore_position = []
        self._restore_alignment = None

        self.tabs = QTabWidget()
        self.tabs.addTab(self.detector_panel, "Plot")
        self.tabs.addTab(QWidget(), "Strips/Pixels")
        self.tabs.addTab(QWidget(), "Parameters")
        self.tabs.addTab(QWidget(), "Commanding")

        # self.setCentralWidget(self.detector_panel)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.tabs)
        
        # self.layout.addWidget(self.detector_panel)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        logging.debug("closing popout")
        self.grid_display._add_to_layout(self.detector_panel)
        # self.grid_display.show()
        # self.detector_panel.popout = None
        # self.detector_panel.popped = False

        self.detector_panel.handlePopin()

        event.accept()

        
        
class GSECommand(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.setOrganizationName(ORG_NAME)      # set organization name
        QApplication.setApplicationName(APP_NAME)       # set application name
        # self.settings = self._restoreSettings()         # restore old settings

        self.setGeometry(100,100,1280,800)
        self.setWindowTitle(APP_NAME)

        fmtrif = FormatterUDPInterface(addr="127.0.0.1", port=9999, logging=True, logfilename=None)

        self.setCentralWidget(GlobalCommandPanel(self, name="Command", formatter_if=fmtrif))