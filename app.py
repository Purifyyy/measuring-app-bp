import pyvisa
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle

from multimeter_HMC8012 import DigitalMultimeterHMC8012
from powersupply_HMC804x import PowerSupplyHMC804x


available_power_supplies = {
    "HMC8043": PowerSupplyHMC804x
}

available_multimeters = {
    "HMC8012": DigitalMultimeterHMC8012
}


class Application(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.HMC8043_common_commands_list = None
        self.HMC8043_common_commands = None
        self.multimeter = None
        self.power_supply = None
        self.device_options = self.get_options()

        self.powersupply_button = QPushButton()
        self.powersupply_menu = QComboBox()
        self.multimeter_button = QPushButton()
        self.multimeter_menu = QComboBox()
        self.connect_section = self.make_connect_tab()
        self.tab_bar = self.make_tab_bar()

        self.setWindowTitle("Measure it")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        layout = QGridLayout()

        layout.addWidget(self.connect_section, 0, 0)
        layout.addWidget(self.tab_bar, 1, 0)

        self.setLayout(layout)

    def handle_error(self, error):
        errmsg = QMessageBox()
        errmsg.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        errmsg.setIcon(QMessageBox.Critical)
        errmsg.setText(error)
        errmsg.setWindowTitle("Error")
        errmsg.exec()

    def make_connect_tab(self):
        device_box = QGroupBox("Devices")
        device_layout = QGridLayout()

        device_layout.addWidget(QLabel("Power Supply"), 0, 0)

        self.powersupply_menu.addItems(self.device_options)
        self.powersupply_menu.setCurrentIndex(-1)
        device_layout.addWidget(self.powersupply_menu, 0, 1)

        self.powersupply_button.setText("Connect")
        self.powersupply_button.clicked.connect(self.connect_power_supply)
        device_layout.addWidget(self.powersupply_button, 0, 2)

        device_layout.addWidget(QLabel("Multimeter"), 1, 0)

        self.multimeter_menu.addItems(self.device_options)
        self.multimeter_menu.setCurrentIndex(-1)
        device_layout.addWidget(self.multimeter_menu, 1, 1)

        self.multimeter_button.setText("Connect")
        self.multimeter_button.clicked.connect(self.connect_multimeter)
        device_layout.addWidget(self.multimeter_button, 1, 2)

        device_box.setLayout(device_layout)
        return device_box

    def make_tab_bar(self):
        bar = QTabWidget()
        bar.setMovable(True)
        bar.setVisible(False)
        return bar

    def connect_power_supply(self):
        device_chosen = self.powersupply_menu.currentText()
        if available_power_supplies.get(device_chosen) is not None:
            address = self.device_options.get(device_chosen)
            if address is not None:
                print("pripajam " + device_chosen + " na adrese " + address)
                self.power_supply = available_power_supplies[device_chosen](address)
                self.add_device_tab(device_chosen)
        else:
            self.handle_error("No such power supply available!")

    def connect_multimeter(self):
        device_chosen = self.multimeter_menu.currentText()
        if available_multimeters.get(device_chosen) is not None:
            address = self.device_options.get(device_chosen)
            if address is not None:
                print("pripajam " + device_chosen + " na adrese " + address)
                self.multimeter = available_multimeters[device_chosen](address)
                self.add_device_tab(device_chosen)
        else:
            self.handle_error("No such multimeter available!")

    def add_device_tab(self, device_chosen):
        try:
            eval("self.add_" + device_chosen + "_tab()")
        except AttributeError:
            self.handle_error("Tab for this device is not available!")

    def send_HMC8043_common_command(self):
        inst = self.HMC8043_common_commands.currentText()
        print(self.HMC8043_common_commands_list[inst]())


    def add_HMC8043_tab(self):
        device_tab = QWidget()
        device_tab_layout = QGridLayout()
        self.HMC8043_common_commands_list = {
            "*TST?": self.power_supply.tst,
            "*RST": self.power_supply.rst,
            "SYSTem:LOCal": self.power_supply.local,
            "SYSTem:REMote": self.power_supply.remote
        }
        self.HMC8043_common_commands = QComboBox()
        self.HMC8043_common_commands.addItems(self.HMC8043_common_commands_list)
        self.HMC8043_common_commands.setCurrentIndex(-1)
        device_tab_layout.addWidget(self.HMC8043_common_commands, 0, 0)

        common_commands_button = QPushButton()
        common_commands_button.setText("Apply")
        common_commands_button.clicked.connect(self.send_HMC8043_common_command)
        device_tab_layout.addWidget(common_commands_button, 0, 1)

        if self.tab_bar.isHidden():
            self.tab_bar.show()

        device_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(device_tab, "HMC8043")

    def add_HMC8012_tab(self):
        print("making hmc8012 tab")

    def get_options(self):
        # Vytvor dictionary device_name:address
        devices = {
            # "HMC8012": "01234",
            # "HMC8043": "56789"
        }
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        for res in resources:
            inst = rm.open_resource(res)
            devices[((inst.query("*IDN?")).split(","))[1]] = res
            inst.close()
        rm.close()
        return devices

