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



class tabdemo(QTabWidget):
    def __init__(self, parent=None):
        super(tabdemo, self).__init__(parent)
        dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
        self.setStyleSheet(dark_stylesheet)
        self.setMovable(True)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.addTab(self.tab3, "Tab 3")
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.setWindowTitle("tab demo")

    def hideit(self):
        self.setTabVisible(2, False)

    def showit(self):
        self.setTabVisible(2, True)

    def tab1UI(self):
        layout = QFormLayout()
        layout.addRow("Name", QLineEdit())
        layout.addRow("Address", QLineEdit())
        bttn = QPushButton("HIDE")
        bttn.clicked.connect(self.hideit)
        layout.addRow("hide it", bttn)
        self.setTabText(0, "Contact Details")
        self.tab1.setLayout(layout)

    def tab2UI(self):
        layout = QFormLayout()
        sex = QHBoxLayout()
        sex.addWidget(QRadioButton("Male"))
        sex.addWidget(QRadioButton("Female"))
        layout.addRow(QLabel("Sex"), sex)
        layout.addRow("Date of Birth", QLineEdit())
        bttn = QPushButton("SHOW")
        bttn.clicked.connect(self.showit)
        layout.addRow("hide it", bttn)
        self.setTabText(1, "Personal Details")
        self.tab2.setLayout(layout)

    def tab3UI(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("subjects"))
        layout.addWidget(QCheckBox("Physics"))
        layout.addWidget(QCheckBox("Maths"))
        self.setTabText(2, "Education Details")
        self.tab3.setLayout(layout)

