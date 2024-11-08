import sys, os, pathlib

from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QComboBox, QLabel, QPushButton, QApplication, QRadioButton, QButtonGroup, QLineEdit, QListWidget
from PyQt6 import QtCore, QtGui

import FoGSE.communication as comm
from FoGSE.io.newest_data import newest_data_dir

class CommandUplinkWidget(QWidget):
    """
    `CommandUplinkWidget` provides a unified interface to send any uplink commands to the Formatter. This is enabled by `communication.FormatterUDPInterface`, which handles the socket I/O. The widget is laid out horizontally on the screen and provides a series of dropdown menus used to build up a valid command bitstring.

    :param name: Unique name of this panel interface.
    :type name: str
    :param label: Label for this interface (for display).
    :type label: str
    :param cmddeck: Command deck object (instantiated using .json config files), used for command validation and filtering.
    :type cmddeck: communication.UplinkCommandDeck
    :param fmtrif: Formatter UDP interface object.
    :type fmtrif: communication.FormatterUDPInterface
    """

    def __init__(self, parent=None, name="PLACEHOLDER", configuration=None, formatter_if=None):
        QWidget.__init__(self, parent)

        self.name = name
        self.label = "Global command uplink"

        # build and validate list of allowable uplink commands
        # self.cmddeck = comm.UplinkCommandDeck("config/all_systems.json", "config/all_commands.json")
        # self.cmddeck = comm.UplinkCommandDeck("foxsi4-commands/all_systems.json", "foxsi4-commands/commands.json")
        

        # open UDP socket to remote
        # self.fmtrif = comm.FormatterUDPInterface(addr="127.0.0.1", port=9999, logging=True, logfilename=None)
        if formatter_if is None:
            self.fmtrif = comm.FormatterUDPInterface()
        else:
            self.fmtrif = formatter_if
        
        self.cmddeck = self.fmtrif.deck

        self.command_interface = self.fmtrif.command_interface
        # track current command being assembled in interface
        self._working_command = []
        
        # group all UI elements in widget
        self.cmd_box = QGroupBox(self.label)

        # make UI widgets:
        min_scroll_height = 400
        self.box_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()
        self.system_label = QLabel("System")
        self.system_combo_box = QListWidget()
        self.command_label = QLabel("Command")
        self.command_combo_box = QListWidget()
        # self.args_label = QLabel("Argument")
        # self.command_args_text = QLineEdit()
        self.send_label = QLabel("")
        self.command_send_button = QPushButton("Send command")

        self._raw, self._check = "Raw: ", "Name: "
        self.system_raw_label = QLabel(self._raw, self)
        self.system_raw_value = QLabel("", self)
        self.system_raw_value.setStyleSheet("font-family: PT Mono}")
        self.system_raw_value.setEnabled(False)
        self.system_name_label = QLabel(self._check, self)
        self.system_name_value = QLabel("", self)
        self.system_name_value.setStyleSheet("font-family: PT Mono}")
        self.system_name_value.setEnabled(False)

        self.command_raw_label = QLabel(self._raw, self)
        self.command_raw_value = QLabel("", self)
        self.command_raw_value.setStyleSheet("font-family: PT Mono}")
        self.command_raw_value.setEnabled(False)
        self.command_name_label = QLabel(self._check, self)
        self.command_name_value = QLabel("", self)
        self.command_name_value.setStyleSheet("font-family: PT Mono}")
        self.command_name_value.setEnabled(False)

        self.command_interface_label = QLabel("Command interface:", self)
        self.command_interface_value = QLabel(self.command_interface, self)
        self.command_interface_value.setStyleSheet("font-family: PT Mono}")
        self.command_interface_value.setEnabled(False)

        self.current_log_folder_label = QLabel("Currently logging to:", self)
        self.current_log_folder_value = QLabel(os.path.basename(os.path.normpath(newest_data_dir())), self)
        self.current_log_folder_value.setStyleSheet("font-family: PT Mono}")
        self.current_log_folder_value.setEnabled(False)

        # populate dialogs with valid lists:
        for sys in self.cmddeck.systems:
            if len(self.cmddeck.get_commands_for_system(sys.name)) != 0:
                self.system_combo_box.addItem(sys.name.lower())

        # for cmd in self.cmddeck[].commands:
        #     self.command_combo_box.addItem(cmd.name)

        # populate layout:
        self.grid_layout.addWidget(
            self.system_label,
            0,0,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.system_combo_box.setMinimumWidth(160)
        self.system_combo_box.setMinimumHeight(min_scroll_height)
        self.grid_layout.addWidget(
            self.system_combo_box,
            1,0,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.grid_layout.addWidget(
            self.system_raw_label,
            2,0,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.system_raw_value,
            2,1,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.system_name_label,
            3,0,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.system_name_value,
            3,1,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_label,
            0,2,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_combo_box,
            1,2,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.command_combo_box.setMinimumWidth(270)
        self.command_combo_box.setMinimumHeight(min_scroll_height)
        self.grid_layout.addWidget(
            self.command_raw_label,
            2,2,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_raw_value,
            2,3,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_name_label,
            3,2,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_name_value,
            3,3,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.send_label,
            0,4,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_send_button,
            1,4,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.grid_layout.addWidget(
            self.command_interface_label,
            5,0,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.command_interface_value,
            5,2,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.current_log_folder_label,
            6,0,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.grid_layout.addWidget(
            self.current_log_folder_value,
            6,2,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )

        self.grid_layout.setRowMinimumHeight(4,40)

        # somehow, this aligns the Widgets in the grid top-left:
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(),1)
        self.grid_layout.setColumnStretch(self.grid_layout.columnCount(),1)

        # add grid layout to box
        self.cmd_box.setLayout(self.grid_layout)

        # add box to a global layout for whole self widget
        self.box_layout.addWidget(self.cmd_box)
        self.box_layout.addStretch(10)
        self.setLayout(self.box_layout)

        # hook up callbacks
        self.system_combo_box.itemSelectionChanged.connect(self.systemComboBoxClicked)
        self.command_combo_box.itemSelectionChanged.connect(self.commandComboBoxClicked)
        self.command_send_button.clicked.connect(self.commandSendButtonClicked)

        # disable downstream command pieces (until selection is made)
        self.command_combo_box.setEnabled(False)
        # self.command_args_text.setEnabled(False)
        self.command_send_button.setEnabled(False)
    
    def systemComboBoxClicked(self):
        self.command_combo_box.setEnabled(False)
        # self.command_args_text.setEnabled(False)
        self.command_send_button.setEnabled(False)
        cmds = self.cmddeck.get_commands_for_system(self.system_combo_box.currentItem().text())
        names = [cmd.name for cmd in cmds]
        
        # start working command with address of selected system
        self._working_command = []
        sys = self.cmddeck.get_system_by_name(self.system_combo_box.currentItem().text())
        self._working_command.append(sys.addr)

        self.command_combo_box.clear()
        for i, cmd in enumerate(cmds):
            self.command_combo_box.addItem(cmd.name)
            # for future: this is 
            self.command_combo_box.item(i).setForeground(QtGui.QColor(round(255*i/len(cmds))))

        self.command_combo_box.setEnabled(True)
        self.system_raw_value.setText(hex(sys.addr))
        self.system_name_value.setText(self.cmddeck.get_system_by_addr(sys.addr).name)
        self.command_raw_value.setText("")
        self.command_name_value.setText("")

    def commandComboBoxClicked(self):
        # self.command_args_text.setEnabled(False)
        self.command_send_button.setEnabled(False)
        sys = self.cmddeck.get_system_by_name(self.system_combo_box.currentItem().text())

        if sys is None:
            return

        cmd = self.cmddeck.get_command_for_system(self.system_combo_box.currentItem().text(), self.command_combo_box.currentItem().text())
        if cmd is None:
            return

        self._working_command = [sys.addr,cmd.hex]

        if cmd.arg_len > 0:
            # self.command_args_text.setEnabled(True)
            # todo: some arg validation set up here. Implement in UplinkCommandDeck.
            pass
        else:
            self.command_send_button.setEnabled(True)

        self.command_raw_value.setText(hex(cmd.hex))
        self.command_name_value.setText(self.cmddeck.get_command_for_system(system=sys.addr, command=cmd.hex).name)

    def commandSendButtonClicked(self, events):
        print("validating command...")
        # todo: validate
        if len(self._working_command) == 2:
            self.fmtrif.submit_uplink_command(self._working_command[0], self._working_command[1])
        else:
            print(self._working_command)
            raise Exception("wrong length working command: " + str(len(self._working_command)))

        self.command_combo_box.setEnabled(False)
        self.command_send_button.setEnabled(False)
    
    def commandInterfaceButtonClicked(self, events):
        print("switched to commanding mode:", self.command_mode_button_group.checkedButton().text())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Left:
            self.system_combo_box.setFocus()
        if event.key() == QtCore.Qt.Key.Key_Right:
            if self.command_combo_box.isEnabled():
                self.command_combo_box.setFocus()
                self.command_combo_box.setCurrentRow(0)


if __name__ == "__main__":
    # if (len(sys.argv)) > 0:
    app = QApplication([])

    # c = comm.FormatterUDPInterface(configfile="foxsi4-commands/foxsimile_systems.json", command_interface="uplink")
    # c = comm.FormatterUDPInterface()
    # window = CommandUplinkWidget(formatter_if=c)
    window = CommandUplinkWidget()
    window.show()
    sys.exit(app.exec())