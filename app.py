import pyvisa
from PyQt5.QtWidgets import *
import qdarkstyle


class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.connect_tab = QWidget()
        self.powersupply_button = QPushButton()
        self.powersupply_menu = QComboBox()

        self.device_options = self.get_options()
        self.setWindowTitle("Measure it")
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
        self.setStyleSheet(dark_stylesheet)
        layout = QGridLayout()

        self.device_tab()
        layout.addWidget(self.connect_tab, 0, 0)

        self.setLayout(layout)

    def device_tab(self):
        device_box = QGroupBox("Devices")
        device_layout = QGridLayout()

        device_layout.addWidget(QLabel("Power Supply"), 0, 0)

        self.powersupply_menu.addItems(self.device_options)
        self.powersupply_menu.setPlaceholderText("-")
        device_layout.addWidget(self.powersupply_menu, 0, 1)

        self.powersupply_button.setText("Connect")
        self.powersupply_button.clicked.connect(self.connect_power_supply)
        device_layout.addWidget(self.powersupply_button, 0, 2)

        device_box.setLayout(device_layout)
        self.connect_tab = device_box

    def connect_power_supply(self):
        print(self.device_options.get(self.powersupply_menu.currentText()))

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

