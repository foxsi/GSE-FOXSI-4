import logging, json, sys
import FoGSE.parameters as params
import FoGSE.communication as comm

from PyQt6 import QtWidgets, QtGui, QtCore

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class SystemConfiguration():
    """
    SystemConfiguration is a container for storing and safely modifying software-wide properties, like log file paths, Formatter address, and flight mode.
    """
    def __init__(self, settings_file: str="./config/settings.json", formatter_if=comm.FormatterUDPInterface()):
        settings_dict = {}
        self._formatter_if = formatter_if

        try:
            with open(settings_file, 'r') as file:
                settings_dict = json.load(file)
        except EnvironmentError:
            print("couldn't open settings file")

        # define attributes of self based on names in settings_dict
        self.set_uplink_addr(settings_dict["uplink_addr"])
        self.set_uplink_port(settings_dict["uplink_port"])
        self.set_downlink_addr(settings_dict["downlink_addr"])
        self.set_downlink_port(settings_dict["downlink_port"])
        self.set_logger_addr(settings_dict["logger_addr"])
        self.set_flight(settings_dict["flight"])
        self.set_arm_flight(settings_dict["arm_flight"])
        self.set_systems_path(settings_dict["systems_path"])
        self.set_command_path(settings_dict["command_path"])
        self.set_logger_executable_path(settings_dict["logger_executable_path"])
        self.set_logger_log_path(settings_dict["logger_log_path"])
        self.set_uplink_log_path(settings_dict["uplink_log_path"])
        self.set_error_log_path(settings_dict["error_log_path"])
    
    def set_uplink_addr(self, addr: str):
        self.uplink_addr = addr
        self._formatter_if.change_endpoint(addr, self._formatter_if.formatter_port)

    def set_uplink_port(self, port: int):
        self.uplink_port = port
        self._formatter_if.change_endpoint(self._formatter_if.formatter_ip, port)

    def set_downlink_addr(self, addr: str):
        self.downlink_addr = addr

    def set_downlink_port(self, port: int):
        self.downlink_port = port

    def set_logger_addr(self, addr: str):
        self.logger_addr = addr
        # try to open

    def set_flight(self, flight: bool):
        self.flight = flight
        self.arm = False

    def set_arm_flight(self, arm: bool):
        self.arm = arm

    def set_systems_path(self, systems_path: str):
        self.systems_path = systems_path
        # try to open
        # validate systems and commands

    def set_command_path(self, command_path: str):
        self.command_path = command_path
        # try to open
        # revalidate commands

    def set_logger_executable_path(self, logger_executable_path: str):
        self.logger_executable_path = logger_executable_path
        # try to launch (using appropriate kwargs)

    def set_logger_log_path(self, logger_log_path: str):
        self.logger_log_path = logger_log_path
        # try to open

    def set_uplink_log_path(self, uplink_log_path: str):
        self.uplink_log_path = uplink_log_path
        # try to open

    def set_error_log_path(self, error_log_path: str):
        self.error_log_path = error_log_path
        # try to open

    # def __init__(self, settings_dict: dict=None):
    #     pass



class SettingsPanel(QtWidgets.QWidget):
    def __init__(self, parent, name="PLACEHOLDER", settings_file="./config/settings.json", system_configuration=SystemConfiguration()):
        QtWidgets.QWidget.__init__(self, parent)
        self.name = name
        self.label = "Settings"
        self.system_configuration = system_configuration

        self.open_button = QtWidgets.QPushButton("Open settings...", self)
        self.arm_button = QtWidgets.QCheckBox("Arm for flight", self)
        self.fly_button = QtWidgets.QCheckBox("Flight mode", self)
        self.fly_button.setEnabled(False)

        self.playback_slider = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation.Horizontal, parent=self)

        self.playback_button = QtWidgets.QPushButton("", parent=self)
        self.playback_pause_icon = QtGui.QIcon("assets/icon_pause_col_bg.svg") # put these in memory so we don't do disk I/O every pause/play
        self.playback_play_icon = QtGui.QIcon("assets/icon_play_col_bg.svg")
        self.playback_button.setIcon(self.playback_play_icon)
        self.playback_button.setFixedSize(48,48)
        self.playback_button.setIconSize(QtCore.QSize(48,48))
        self.playback_button.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;}")
        self.do_play = True

        self.group_box = QtWidgets.QGroupBox("Settings", self)
        
        self.inner_layout = QtWidgets.QGridLayout()
        self.inner_layout.addWidget(self.open_button, 0,0,1,4)
        self.inner_layout.addWidget(self.arm_button, 1,0,1,2)
        self.inner_layout.addWidget(self.fly_button, 1,2,1,2)
        self.inner_layout.addWidget(self.playback_button, 2,0,1,1)
        self.inner_layout.addWidget(self.playback_slider, 2,1,1,3)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.inner_layout)
        self.group_box.setLayout(self.layout)

        self.open_button.clicked.connect(self.openSettingsDialog)
        self.arm_button.stateChanged.connect(self.handleFlightButtons)
        self.fly_button.stateChanged.connect(self.handleFlightButtons)
        self.playback_button.clicked.connect(self.handlePlaybackButton)

    def openSettingsDialog(self, event):
        # pass in self (as parent of SettingsDialog) so dialog can modify settings stored here
        dialog = SettingsDialog(self, self.system_configuration) 
        if dialog.exec():
            logging.debug("got settings accept")
        else:
            logging.debug("got settings reject")

    def handleFlightButtons(self, event):
        # enter armed mode
        if self.arm_button.isChecked():
            logging.debug("entering flight arm mode")
            self.fly_button.setEnabled(True)
            self.enterArmedMode()
        
        # exit armed mode
        if not self.arm_button.isChecked():
            logging.debug("exiting flight arm mode")
            self.fly_button.setEnabled(False)
            self.exitArmedMode()
            
        # enter flight mode
        if self.fly_button.isChecked():
            logging.debug("entering flight mode")
            self.arm_button.setEnabled(False)
            self.fly_button.setEnabled(False)
            self.enterFlightMode()

    def handlePlaybackButton(self, event):
        if self.do_play:
            logging.debug("playing data display")
            self.playback_button.setIcon(self.playback_pause_icon)
            self.do_play  = False
        else:
            logging.debug("pausing data display")
            self.playback_button.setIcon(self.playback_play_icon)
            self.do_play  = True
    
    def enterArmedMode(self):
        self.system_configuration.set_arm_flight(True)
        self.playback_slider.setEnabled(False)
   
    def exitArmedMode(self):
        self.system_configuration.set_arm_flight(False)
        self.playback_slider.setEnabled(True)

    def enterFlightMode(self):
        self.system_configuration.set_flight(True)
    


class FilePathLoad(QtWidgets.QWidget):
    def __init__(self, parent, width: int=120, dialog_name: str=""):
        QtWidgets.QWidget.__init__(self, parent)

        self.text_field = QtWidgets.QLineEdit()
        self.text_field.setFixedWidth(width)
        self.browse_button = QtWidgets.QPushButton("Browse...")
        self.dialog_name = dialog_name

        self.layout = QtWidgets.QHBoxLayout()
        # self.layout.addWidget(self.text_field, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.browse_button)
        self.setLayout(self.layout)
        # self.setMaximumHeight(50)

        self.browse_button.clicked.connect(self.handleBrowsePush)

    def handleBrowsePush(self, event):
        print("select file")

        dialog = QtWidgets.QFileDialog(self, caption=self.dialog_name)
        
        if dialog.exec():
            filenames = dialog.selectedFiles()

    def handleTextEntry(self, event):
        pass



class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, system_configuration: SystemConfiguration):
        QtWidgets.QDialog.__init__(self, parent)

        self.system_configuration = system_configuration
        basewidth = 200

        self.setWindowTitle("Settings")
        self.terminal_buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel, self)

        self.uplink_addr_field = QtWidgets.QLineEdit()
        self.uplink_addr_field.setText(self.system_configuration.uplink_addr)
        self.uplink_port_field = QtWidgets.QLineEdit()
        self.uplink_port_field.setText(str(self.system_configuration.uplink_port))
        self.downlink_port_field = QtWidgets.QLineEdit()
        self.downlink_port_field.setText(str(self.system_configuration.downlink_port))
        self.socket_file_field = FilePathLoad(self, width=basewidth, dialog_name="Select socket file path")
        self.socket_file_field.text_field.setText(self.system_configuration.logger_addr)
        self.systems_path_field = FilePathLoad(self, width=basewidth, dialog_name="Select systems list file")
        self.systems_path_field.text_field.setText(self.system_configuration.systems_path)
        self.commands_path_field = FilePathLoad(self, width=basewidth, dialog_name="Select commands list file")
        self.commands_path_field.text_field.setText(self.system_configuration.command_path)
        self.logger_executable_path_field = FilePathLoad(self, width=basewidth, dialog_name="Logger executable file")
        self.logger_executable_path_field.text_field.setText(self.system_configuration.logger_executable_path)
        self.logger_log_path_field = FilePathLoad(self, width=basewidth, dialog_name="Downlink log file path")
        self.logger_log_path_field.text_field.setText(self.system_configuration.logger_log_path)
        self.uplink_log_path_field = FilePathLoad(self, width=basewidth, dialog_name="Uplink log file path")
        self.uplink_log_path_field.text_field.setText(self.system_configuration.uplink_log_path)
        self.error_log_path_field = FilePathLoad(self, width=basewidth, dialog_name="Error log file path")
        self.error_log_path_field.text_field.setText(self.system_configuration.error_log_path)

        self.load_settings_path_button = QtWidgets.QPushButton("Load settings file...")

        self.network_control_layout = QtWidgets.QGridLayout()
        self.software_configuration_layout = QtWidgets.QGridLayout()
        self.network_control_layout.addWidget(QtWidgets.QLabel("Formatter IP address"),      0,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.network_control_layout.addWidget(self.uplink_addr_field,              0,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.network_control_layout.addWidget(QtWidgets.QLabel("Uplink port"),               1,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.network_control_layout.addWidget(self.uplink_port_field,              1,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.network_control_layout.addWidget(QtWidgets.QLabel("Downlink (local) port"),     2,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.network_control_layout.addWidget(self.downlink_port_field,            2,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.network_control_layout.addWidget(QtWidgets.QLabel("Logger socket file path"),   3,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.network_control_layout.addWidget(self.socket_file_field,              3,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.network_control_layout.setRowStretch(self.network_control_layout.rowCount(), 1)

        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Systems list file path"),    0,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.systems_path_field,             0,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Commands list file path"),   1,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.commands_path_field,            1,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Logger executable path"),    2,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.logger_executable_path_field,   2,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Downlink log file path"),    3,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.logger_log_path_field,          3,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Uplink log file path"),      4,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.uplink_log_path_field,          4,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.addWidget(QtWidgets.QLabel("Error log file path"),       5,0,1,1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.software_configuration_layout.addWidget(self.error_log_path_field,           5,1,1,1, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.software_configuration_layout.setRowStretch(self.software_configuration_layout.rowCount(), 1)
        for i in range(self.software_configuration_layout.rowCount()):
            self.software_configuration_layout.setRowMinimumHeight(i,50)
        self.software_configuration_layout.setVerticalSpacing(5)
        
        self.inner_layout = QtWidgets.QGridLayout()
        self.layout = QtWidgets.QVBoxLayout()
        self.group_box = QtWidgets.QGroupBox("Settings")
        
        self.inner_layout.addLayout(self.network_control_layout, 0,0,1,1)
        self.inner_layout.addLayout(self.software_configuration_layout, 0,1,1,1)
        self.inner_layout.addWidget(self.load_settings_path_button, 1,1,1,2)
        self.group_box.setLayout(self.inner_layout)

        self.layout.addWidget(self.group_box)
        self.layout.addWidget(self.terminal_buttons)
        self.setLayout(self.layout)

        self.uplink_addr_field.textChanged.connect(self.handleUplinkAddrChanged)
        self.uplink_port_field.textChanged.connect(self.handleUplinkPortChanged)
        self.downlink_port_field.textChanged.connect(self.handleDownlinkPortChanged)
        self.socket_file_field.text_field.textChanged.connect(self.handleLoggerSocketFileChanged)
        self.systems_path_field.text_field.textChanged.connect(self.handleSystemsPathChanged)
        self.commands_path_field.text_field.textChanged.connect(self.handleCommandsPathChanged)
        self.logger_executable_path_field.text_field.textChanged.connect(self.handleLoggerExecutableChanged)
        self.logger_log_path_field.text_field.textChanged.connect(self.handleLoggerLogChanged)
        self.error_log_path_field.text_field.textChanged.connect(self.handleErrorLogPathChanged)

        self.terminal_buttons.accepted.connect(self.accept)
        self.terminal_buttons.rejected.connect(self.reject)
        self.load_settings_path_button.clicked.connect(self.handleLoadSettings)

        # settings dialog should also have a modal file browser to load a settings json file
    
    def handleLoadSettings(self, events):
        # dialog = QFileDialog(self, caption=self.dialog_name)
        # if dialog.exec():
        #     filenames = dialog.selectedFiles()
        filename = QtWidgets.QFileDialog.getOpenFileName(self,filter="JSON file (*.json)")[0]
        logging.debug("selected " + str(filename))

    # for the below, input validation should happen in SystemConfiguration
    def handleUplinkAddrChanged(self, events):
        self.system_configuration.set_uplink_addr(self.uplink_addr_field.text())
    def handleUplinkPortChanged(self, events):
        self.system_configuration.set_uplink_port(self.uplink_port_field.text())
    def handleDownlinkPortChanged(self, events):
        self.system_configuration.set_downlink_port(self.downlink_port_field.text())

    def handleLoggerSocketFileChanged(self, events):
        self.system_configuration.set_logger_addr(self.socket_file_field.text_field.text())
    def handleSystemsPathChanged(self, events):
        self.system_configuration.set_systems_path(self.systems_path_field.text_field.text())
    def handleCommandsPathChanged(self, events):
        self.system_configuration.set_command_path(self.commands_path_field.text_field.text())
    def handleLoggerExecutableChanged(self, events):
        self.system_configuration.set_logger_executable_path(self.logger_executable_path_field.text_field.text())
    def handleLoggerLogChanged(self, events):
        self.system_configuration.set_logger_log_path(self.logger_log_path_field.text_field.text())
    def handleErrorLogPathChanged(self, events):
        self.system_configuration.set_error_log_path(self.error_log_path_field.text_field.text())


# pass as init args to Detector...View objects
class DetectorEssentials():
    def __init__(self, name="PLACEHOLDER", label="Placeholder", system_configuration: SystemConfiguration=None, formatter_interface=comm.FormatterUDPInterface()):
        self.name = name
        self.label = label
        self.system_configuration = system_configuration
        self.formatter_interface = formatter_interface