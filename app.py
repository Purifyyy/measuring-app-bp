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
        self.power_supply_tab = None
        self.multimeter_tab = None
        self.power_supply = None
        self.is_power_supply_connected = False
        self.multimeter = None
        self.is_multimeter_connected = False

        self.device_options = self.get_device_options()

        self.powersupply_button = None
        self.powersupply_menu = None
        self.multimeter_button = None
        self.multimeter_menu = None
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

        self.powersupply_menu = QComboBox()
        self.powersupply_menu.addItems(self.device_options)
        self.powersupply_menu.setCurrentIndex(-1)
        device_layout.addWidget(self.powersupply_menu, 0, 1)

        self.powersupply_button = QPushButton()
        self.powersupply_button.setText("Connect")
        self.powersupply_button.clicked.connect(self.connect_power_supply)
        device_layout.addWidget(self.powersupply_button, 0, 2)

        device_layout.addWidget(QLabel("Multimeter"), 1, 0)

        self.multimeter_menu = QComboBox()
        self.multimeter_menu.addItems(self.device_options)
        self.multimeter_menu.setCurrentIndex(-1)
        device_layout.addWidget(self.multimeter_menu, 1, 1)

        self.multimeter_button = QPushButton()
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
        if self.is_power_supply_connected is False:
            if available_power_supplies.get(device_chosen) is not None:
                address = self.device_options.get(device_chosen)
                if address is not None:
                    print("pripajam " + device_chosen + " na adrese " + address)
                    self.power_supply = available_power_supplies[device_chosen](address)
                    self.add_device_tab(device_chosen)
                    self.is_power_supply_connected = True
                    self.powersupply_button.setText("Disconnect")
                    self.powersupply_menu.setDisabled(True)
                    self.switch_tab_bar()
            else:
                self.handle_error("No such power supply available!")
        else:
            del self.power_supply
            self.power_supply = None
            self.is_power_supply_connected = False
            self.powersupply_button.setText("Connect")
            self.tab_bar.removeTab(self.tab_bar.indexOf(self.power_supply_tab))
            self.power_supply_tab.close()
            self.powersupply_menu.setDisabled(False)
            self.switch_tab_bar()

    def connect_multimeter(self):
        device_chosen = self.multimeter_menu.currentText()
        if self.is_multimeter_connected is False:
            if available_multimeters.get(device_chosen) is not None:
                address = self.device_options.get(device_chosen)
                if address is not None:
                    print("pripajam " + device_chosen + " na adrese " + address)
                    self.multimeter = available_multimeters[device_chosen](address)
                    self.add_device_tab(device_chosen)
                    self.is_multimeter_connected = True
                    self.multimeter_button.setText("Disconnect")
                    self.multimeter_menu.setDisabled(True)
                    self.switch_tab_bar()
            else:
                self.handle_error("No such multimeter available!")
        else:
            del self.multimeter
            self.multimeter = None
            self.is_multimeter_connected = False
            self.multimeter_button.setText("Connect")
            self.tab_bar.removeTab(self.tab_bar.indexOf(self.multimeter_tab))
            self.multimeter_tab.close()
            self.multimeter_menu.setDisabled(False)
            self.switch_tab_bar()

    def switch_tab_bar(self):
        if self.tab_bar.isHidden():
            self.tab_bar.show()
        else:
            if self.tab_bar.count() == 0:
                self.tab_bar.setVisible(False)

    def add_device_tab(self, device_chosen):
        try:
            eval("self.add_" + device_chosen + "_tab()")
        except AttributeError:
            self.handle_error("Tab for this device is not available!")

    def send_common_command(self, device_common_commands, device_common_commands_list):
        inst = device_common_commands.currentText()
        if inst != '':
            res = device_common_commands_list[inst]()
            self.evaluate_method_call(res)

    def evaluate_method_call(self, res):
        if res[0] is not True:
            self.handle_error(res[2])
        else:
            if res[1] == "Query":
                print(res[2])
            else:
                print("write success")

    def add_HMC8043_tab(self):
        self.power_supply_tab = QWidget()
        self.power_supply_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()
        HMC8043_common_commands_list = self.create_common_commands_list(self.power_supply)
        HMC8043_common_commands = QComboBox()
        HMC8043_common_commands.addItems(HMC8043_common_commands_list)
        HMC8043_common_commands.setCurrentIndex(-1)
        device_tab_layout.addWidget(HMC8043_common_commands, 0, 0)

        common_commands_button = QPushButton()
        common_commands_button.setText("Apply")
        common_commands_button.clicked.connect(lambda: self.send_common_command(HMC8043_common_commands,
                                                                                HMC8043_common_commands_list))
        device_tab_layout.addWidget(common_commands_button, 0, 1)

        self.switch_tab_bar()

        self.power_supply_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.power_supply_tab, "HMC8043")

    def add_HMC8012_tab(self):
        self.multimeter_tab = QWidget()
        self.multimeter_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()
        self.HMC8012_common_commands_list = self.create_common_commands_list(self.multimeter)
        self.HMC8012_common_commands = QComboBox()
        self.HMC8012_common_commands.addItems(self.HMC8012_common_commands_list)
        self.HMC8012_common_commands.setCurrentIndex(-1)
        device_tab_layout.addWidget(self.HMC8012_common_commands, 0, 0)

        common_commands_button = QPushButton()
        common_commands_button.setText("Apply")
        common_commands_button.clicked.connect(lambda: self.send_common_command(self.HMC8012_common_commands,
                                                                                self.HMC8012_common_commands_list))
        device_tab_layout.addWidget(common_commands_button, 0, 1)

        self.switch_tab_bar()

        self.multimeter_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.multimeter_tab, "HMC8012")

    def create_common_commands_list(self, device):
        cmds_list = {
            "*TST?": device.tst,
            "*RST": device.rst,
            "SYSTem:LOCal": device.local,
            "SYSTem:REMote": device.remote
        }
        return cmds_list

    def get_device_options(self):
        # Vytvor dictionary device_name:address
        devices = {
            "HMC8012": "01234",
            "HMC8043": "56789"
        }
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        for res in resources:
            inst = rm.open_resource(res)
            devices[((inst.query("*IDN?")).split(","))[1]] = res
            inst.close()
        rm.close()
        return devices

