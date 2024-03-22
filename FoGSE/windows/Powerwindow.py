import sys
from collections import namedtuple

from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGroupBox, QCheckBox, QGridLayout, QVBoxLayout, QApplication

from FoGSE.readers.PowerReader import PowerReader

import FoGSE.configuration as config
import FoGSE.communication as comm

class PowerSystem:
    """
    `PowerSystem` is a wrapper around system-specific data to help `PowerMonitorView`.
    """
    def __init__(self, name="PLACEHOLDER", label="placeholder", parent=None, group=None,
                current=0, voltage=0, staleness=1, current_range=(), voltage_range=()):
        self.name = name
        self.label = QLabel(label)
        self.label.setFixedWidth(100)

        self.indicator = QPushButton("", parent=parent)
        self.indicator.setIcon(QtGui.QIcon("./assets/icon_unknown_col_bg.svg"))
        self.indicator.setFixedSize(24,24)
        self.indicator.setIconSize(QtCore.QSize(24,24))
        self.indicator.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;}")

        self.voltage_label = QLineEdit("?\tV", parent=parent)
        self.voltage_label.setFixedWidth(80)
        self.voltage_label.setEnabled(False)

        self.current_label = QLineEdit("?\tmA", parent=parent)
        self.current_label.setFixedWidth(80)
        self.current_label.setEnabled(False),
        
        self.on_button = QCheckBox("", parent=parent)
        self.on_button.setEnabled(False)
        
        self.group=group

        self.current = current
        self.voltage = voltage
        self.staleness = staleness
        self.current_range = current_range
        self.voltage_range = voltage_range

        self.last_state = False


class PowerMonitorView(QWidget):
    """
    `PowerMonitorView` provides an interface to onboard power status and basic control of the power system.
    """

    def __init__(self, parent=None, name="PLACEHOLDER", reader=None, data_file=None, configuration=config.SystemConfiguration(), formatter_if=comm.FormatterUDPInterface()):
        QWidget.__init__(self, parent)

        self.name = name
        self.label = "Power monitor"

        if data_file is not None:
            # probably the main way to use it
            self.reader = PowerReader(data_file)
        elif reader is not None:
            # useful for testing and if multiple windows need to share the same file
            self.reader = reader
        else:
            print("How do I read the RTD data?")

        self.reader.value_changed_collection.connect(self.update)

        self.cmddeck = formatter_if.deck
        self.fmtrif = formatter_if
        
        # group all UI elements in widget
        self.cmd_box        = QGroupBox(self.label)

        # 
        self.box_layout     = QVBoxLayout()

        # 
        self.arm_button = QtWidgets.QCheckBox("Arm on/off command", parent=self)
        self.send_button = QPushButton("Send power command", parent=self)

        Group = namedtuple("Group", "box layout")
        self.command_group  = Group(QGroupBox("Command"),    QGridLayout())
        self.cdte_group     = Group(QGroupBox("CdTe"),       QGridLayout())
        self.cmos_group     = Group(QGroupBox("CMOS"),       QGridLayout())
        self.timepix_group  = Group(QGroupBox("Timepix"),    QGridLayout())
        self.saas_group     = Group(QGroupBox("SAAS"),       QGridLayout())
        self.reg_group      = Group(QGroupBox("Regulator"),  QGridLayout())

        self.power_system_rows = {
            "cdte": {
                "cdtede": PowerSystem(
                    name="cdtede",
                    label="CdTe DE",
                    group=self.cdte_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,4), 
                    voltage_range=(5.5, 5.9)
                ),
                "cdte1": PowerSystem(
                    name="cdte1",
                    label="CdTe 1",
                    group=self.cdte_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                ),
                "cdte2": PowerSystem(
                    name="cdte2",
                    label="CdTe 2",
                    group=self.cdte_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                ),
                "cdte3": PowerSystem(
                    name="cdte3",
                    label="CdTe 3",
                    group=self.cdte_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                ),
                "cdte4": PowerSystem(
                    name="cdte4",
                    label="CdTe 4",
                    group=self.cdte_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                )
            },
            "cmos": {
                "cmos1": PowerSystem(
                    name="cmos1",
                    label="CMOS 1",
                    group=self.cmos_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                ),
                "cmos2": PowerSystem(
                    name="cmos2",
                    label="CMOS 2",
                    group=self.cmos_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,0.2), 
                    voltage_range=(24, 32)
                )
            },
            "timepix": {
                "timepix 5V": PowerSystem(
                    name="timepix",
                    label="Timepix 5V",
                    group=self.timepix_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,3), 
                    voltage_range=(4.7, 5.3)
                ),
                "timepix 12V": PowerSystem(
                    name="timepix",
                    label="Timepix 12V",
                    group=self.timepix_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,1), 
                    voltage_range=(12, 13)
                )
            },
            "saas": {
                "saas computer": PowerSystem(
                    name="saas",
                    label="SAAS computer",
                    group=self.saas_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,3), 
                    voltage_range=(4.7, 5.3)
                ),
                "saas camera": PowerSystem(
                    name="saas",
                    label="SAAS camera",
                    group=self.saas_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,3), 
                    voltage_range=(12, 13)
                )
            },
            "regulators": {
                "regulators": PowerSystem(
                    name="regulators",
                    label="Regulators",
                    group=self.reg_group,
                    parent=self,
                    current=0,
                    voltage=0, 
                    staleness=1, 
                    current_range=(0,3), 
                    voltage_range=(4.7, 5.3)
                ),
            }
        }

        row = 1
        yet_timepix = False
        yet_saas = False

        for outer_key in self.power_system_rows.keys():
            row = 0
            for inner_key in self.power_system_rows[outer_key].keys():
                # add it to layout:
                self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                    self.power_system_rows[outer_key][inner_key].label,
                    row,0,1,1,
                    alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
                self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                    self.power_system_rows[outer_key][inner_key].voltage_label,
                    row,2,1,1,
                    alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
                self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                    self.power_system_rows[outer_key][inner_key].current_label,
                    row,3,1,1,
                    alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
                if "saas" not in inner_key and "timepix" not in inner_key and "regulator" not in inner_key:
                    self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                        self.power_system_rows[outer_key][inner_key].indicator,
                        row,1,1,1,
                        alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                    )
                    self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                        self.power_system_rows[outer_key][inner_key].on_button,
                        row,4,1,1,
                        alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    if "timepix" in inner_key:
                        if not yet_timepix:
                            self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                                self.power_system_rows[outer_key][inner_key].indicator,
                                row,1,2,1,
                                alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                            )
                            self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                                self.power_system_rows[outer_key][inner_key].on_button,
                                row,4,2,1,
                                alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                            )
                            yet_timepix = True
                        else:
                            self.power_system_rows[outer_key][inner_key].on_button.setEnabled(False)
                            self.power_system_rows[outer_key][inner_key].on_button.setVisible(False)
                            self.power_system_rows[outer_key][inner_key].indicator.setEnabled(False)
                            self.power_system_rows[outer_key][inner_key].indicator.setVisible(False)
                    elif "saas" in inner_key:
                        if not yet_saas:
                            self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                                self.power_system_rows[outer_key][inner_key].indicator,
                                row,1,2,1,
                                alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                            )
                            self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                                self.power_system_rows[outer_key][inner_key].on_button,
                                row,4,2,1,
                                alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                            )
                            yet_saas = True
                        else:
                            self.power_system_rows[outer_key][inner_key].on_button.setEnabled(False)
                            self.power_system_rows[outer_key][inner_key].on_button.setVisible(False)
                            self.power_system_rows[outer_key][inner_key].indicator.setEnabled(False)
                            self.power_system_rows[outer_key][inner_key].indicator.setVisible(False)
                    else:
                        # regulator case
                        self.power_system_rows[outer_key][inner_key].group.layout.addWidget(
                            self.power_system_rows[outer_key][inner_key].indicator,
                            row,1,1,1,
                            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                        )
                        self.power_system_rows[outer_key][inner_key].on_button.setEnabled(False)
                        self.power_system_rows[outer_key][inner_key].on_button.setVisible(False)
                        self.power_system_rows[outer_key][inner_key].indicator.setEnabled(False)
                        self.power_system_rows[outer_key][inner_key].indicator.setVisible(True)
                row += 1

        self.command_group.layout.addWidget(
            self.arm_button,
            0,0,1,2,
            alignment=QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.command_group.layout.addWidget(
            self.send_button,
            0,4,1,1,
            alignment=QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        )

        # somehow, this aligns the Widgets in the grid top-left:
        self.cdte_group.layout.setRowStretch(self.cdte_group.layout.rowCount(),1)
        self.cdte_group.layout.setColumnStretch(self.cdte_group.layout.columnCount(),1)
        self.cmos_group.layout.setRowStretch(self.cmos_group.layout.rowCount(),1)
        self.cmos_group.layout.setColumnStretch(self.cmos_group.layout.columnCount(),1)
        self.timepix_group.layout.setRowStretch(self.timepix_group.layout.rowCount(),1)
        self.timepix_group.layout.setColumnStretch(self.timepix_group.layout.columnCount(),1)
        self.saas_group.layout.setRowStretch(self.saas_group.layout.rowCount(),1)
        self.saas_group.layout.setColumnStretch(self.saas_group.layout.columnCount(),1)
        self.reg_group.layout.setRowStretch(self.reg_group.layout.rowCount(),1)
        self.reg_group.layout.setColumnStretch(self.reg_group.layout.columnCount(),1)
        self.command_group.layout.setRowStretch(self.command_group.layout.rowCount(),1)
        self.command_group.layout.setColumnStretch(self.command_group.layout.columnCount(),1)

        # add grid layout to box
        self.cdte_group.box.setLayout(self.cdte_group.layout)
        self.cmos_group.box.setLayout(self.cmos_group.layout)
        self.timepix_group.box.setLayout(self.timepix_group.layout)
        self.saas_group.box.setLayout(self.saas_group.layout)
        self.reg_group.box.setLayout(self.reg_group.layout)
        self.command_group.box.setLayout(self.command_group.layout)

        # # add box to a global layout for whole self widget
        self.box_layout.addWidget(self.command_group.box)
        self.box_layout.addWidget(self.cdte_group.box)
        self.box_layout.addWidget(self.cmos_group.box)
        self.box_layout.addWidget(self.timepix_group.box)
        self.box_layout.addWidget(self.saas_group.box)
        self.box_layout.addWidget(self.reg_group.box)
        self.box_layout.addStretch(10)
        self.setLayout(self.box_layout)

        self.send_button.setEnabled(False)
        self.arm_button.clicked.connect(self.arm_button_clicked)
        self.send_button.clicked.connect(self.send_button_clicked)

        self._system_buttons_were_checked = [False for i in range(9)]
    
    def update(self):
        new_data = self.reader.collection.data
        print(new_data)

    def system_button_clicked(self):
        pass

    def send_button_clicked(self):
        for outer_key in self.power_system_rows.keys():
            for inner_key in self.power_system_rows[outer_key].keys():
                if self.power_system_rows[outer_key][inner_key].on_button.isChecked() != self.power_system_rows[outer_key][inner_key].last_state:
                    self.power_system_rows[outer_key][inner_key].last_state = self.power_system_rows[outer_key][inner_key].on_button.isChecked()
                    self.send(self.power_system_rows[outer_key][inner_key], self.power_system_rows[outer_key][inner_key].on_button.isChecked())

        self.arm_button.setChecked(False)
        self.disarm()

    def arm_button_clicked(self):
        if self.arm_button.isChecked():
            self.arm()
        else:
            self.disarm()

    def arm(self):
        for outer_key in self.power_system_rows.keys():
            for inner_key in self.power_system_rows[outer_key].keys():
                self.power_system_rows[outer_key][inner_key].on_button.setEnabled(True)
        self.send_button.setEnabled(True)

    def disarm(self):
        for outer_key in self.power_system_rows.keys():
            for inner_key in self.power_system_rows[outer_key].keys():
                self.power_system_rows[outer_key][inner_key].on_button.setEnabled(False)
        self.send_button.setEnabled(False)

    def send(self, system, on):
        on_off_str = ("on" if on else "off")
        hk_addr = self.fmtrif.deck.get_system_by_name("housekeeping").addr
        command_str = "set_power_" + system.name + "_" + on_off_str
        command = self.fmtrif.deck.get_command_for_system(hk_addr, command_str)
        print(system.name + " is being turned " + on_off_str)

        self.fmtrif.submit_uplink_command(hk_addr, command.hex)



if __name__ == "__main__":
    data_file = ""
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        print("reading from file: ", data_file)
    else:
        print("usage:\n> python3 FoGSE/windows/Powerwindow.py <path/to/source/datafile>")
        sys.exit()

    app = QApplication([])
    reader = PowerReader(data_file)

    window = PowerMonitorView(reader=reader)
    window.show()
    app.exec()