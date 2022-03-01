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


# class SpinBox(QDoubleSpinBox):
#     stepChanged = pyqtSignal()
#
#     def stepBy(self, step):
#         value = self.value()
#         super(SpinBox, self).stepBy(step)
#         if self.value() != value:
#             self.stepChanged.emit()

# Custom QComboBox, that comes with previously selected index, on currentIndexChanged signal
class ComboBoxWithLast(QComboBox):
    selectedItemChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(ComboBoxWithLast, self).__init__(parent)
        self.lastSelected = ""
        self.currentIndexChanged.connect(self.onChange)

    def onChange(self, text):
        self.selectedItemChanged.emit(self.lastSelected, text)
        self.lastSelected = text


class ButtonWithSwitch(QPushButton):

    def __init__(self, parent=None):
        super(ButtonWithSwitch, self).__init__(parent)
        self.isActivated = False


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

    def send_command(self, func):
        if func is not None:
            res = func()
            self.evaluate_method_call(res)

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

        device_tab_layout.addWidget(QLabel("Selected channel:"), 0, 0)
        channel_box = QComboBox()
        channel_box.addItems(["OUT1", "OUT2", "OUT3"])
        channel_box.setCurrentIndex(0)
        device_tab_layout.addWidget(channel_box, 0, 1)

        HMC8043_common_commands_list, HMC8043_common_commands, common_commands_button = \
            self.create_common_commands_list(self.power_supply)
        device_tab_layout.addWidget(HMC8043_common_commands, 1, 0)
        device_tab_layout.addWidget(common_commands_button, 1, 1)

        # voltage_box = QGroupBox("Voltage options")
        # voltage_layout = QGridLayout()
        # voltage_layout.addWidget(QLabel("Selected channel voltage:"), 0, 0)
        # # volage_value_dialog = QInputDialog.getDouble(minValue=0.000E+00, maxValue=3.2050E+01, value=1.000E+00)
        # voltage_value = SpinBox()
        # voltage_value.setRange(0, 3.2050E+01)
        # voltage_value.setDecimals(3)
        # voltage_value.setValue(0)
        # voltage_value.editingFinished.connect(self.print_value)
        # voltage_value.stepChanged.connect(self.handleSpinChanged)
        # voltage_layout.addWidget(voltage_value)
        #
        # voltage_box.setLayout(voltage_layout)
        # device_tab_layout.addWidget(voltage_box, 2, 0, 1, 2)

        # param = 1
        # fusestate = QPushButton()
        # fusestate.setText("fuse state")
        # fusestate.clicked.connect(lambda: self.send_command(lambda: self.power_supply.set_fuse_state(param, channel_box.currentText())))
        # device_tab_layout.addWidget(fusestate, 2, 0)

        self.switch_tab_bar()

        self.power_supply_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.power_supply_tab, "HMC8043")

    # def print_value(self):
    #     print("setVoltage")
    #
    # def handleSpinChanged(self):
    #     print("stepVoltage")

    def add_HMC8012_tab(self):
        self.multimeter_tab = QWidget()
        self.multimeter_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()

        common_command_box = QGroupBox("Common commands")
        common_command_box_layout = QGridLayout()
        HMC8012_common_commands_list, HMC8012_common_commands, common_commands_button = \
            self.create_common_commands_list(self.multimeter)
        common_command_box_layout.addWidget(HMC8012_common_commands, 0, 0)
        common_command_box_layout.addWidget(common_commands_button, 0, 1)
        common_command_box.setLayout(common_command_box_layout)
        device_tab_layout.addWidget(common_command_box, 0, 0, 1, 1)

        temperature_box = QGroupBox("Temperature settings")
        temperature_box_layout = QGridLayout()
        temperature_box_layout.addWidget(QLabel("Unit:"), 0, 0)
        temperature_unit = QComboBox()
        temp_unit_options = ["Celsius", "Kelvin", "Fahrenheit"]
        temperature_unit.addItems(temp_unit_options)
        temperature_unit.setItemData(0, "C")
        temperature_unit.setItemData(1, "K")
        temperature_unit.setItemData(2, "F")
        temperature_box_layout.addWidget(temperature_unit, 0, 1)
        temperature_unit.setCurrentIndex(-1)
        temperature_box_layout.addWidget(QLabel("Probe:"), 1, 0)
        probe_type = QComboBox()
        probe_type.addItems({
            "RTD",
            "FRTD"
        })
        temperature_box_layout.addWidget(probe_type, 1, 1)
        probe_type.setCurrentIndex(-1)
        temperature_box_layout.addWidget(QLabel("Sensor:"), 2, 0)
        sensor_type = QComboBox()
        sensor_type.addItems({
            "PT100",
            "PT500",
            "PT1000"
        })
        sensor_type.setCurrentIndex(-1)
        temperature_box_layout.addWidget(sensor_type, 2, 1)
        setup_temperature_button = QPushButton()
        setup_temperature_button.setText("Configure")
        setup_temperature_button.clicked.connect(lambda: self.configure_temperature(
            temperature_unit.itemData(temperature_unit.currentIndex()),
            probe_type.currentText(),
            sensor_type.currentText()))
        temperature_box_layout.addWidget(setup_temperature_button, 0, 2, 3, 1)
        temperature_box.setLayout(temperature_box_layout)
        device_tab_layout.addWidget(temperature_box, 0, 1, 1, 1)

        function_box = QGroupBox("Measurement options")
        function_box_layout = QGridLayout()
        function_box_layout.addWidget(QLabel("Selected measurement function:"), 0, 0)
        measurement_function = ComboBoxWithLast()
        measurement_function.addItem("DC V", self.multimeter.measure_voltage_dc)
        measurement_function.addItem("AC V", self.multimeter.measure_voltage_ac)
        measurement_function.addItem("DC I", self.multimeter.measure_current_dc)
        measurement_function.addItem("AC I", self.multimeter.measure_current_ac)
        measurement_function.addItem("Ω", self.multimeter.measure_continuity)
        measurement_function.addItem("CAP", self.multimeter.measure_capacitance)
        # measurement_function.addItem("SENSOR", )
        measurement_function.setCurrentIndex(-1)
        measurement_function.selectedItemChanged.connect(self.configure_multimeter_measurements)
        function_box_layout.addWidget(measurement_function, 0, 1, 1, 2)

        function_box_layout.addWidget(QLabel("Mathematic function:"), 1, 0)
        mathematic_function = QComboBox()
        mathematic_function.addItems([
            "AVERage",
            "LIMit",
            "NULL",
            "DB",
            "DBM",
            "POWer",
        ])
        mathematic_function.setCurrentIndex(-1)
        mathematic_function.currentTextChanged.connect(self.set_mathematic_function)
        function_box_layout.addWidget(mathematic_function, 1, 1)

        activate_mathematic_function = ButtonWithSwitch()
        activate_mathematic_function.setText("Activate")
        activate_mathematic_function.clicked.connect(self.activate_calc_function)
        function_box_layout.addWidget(activate_mathematic_function, 1, 2)

        function_box.setLayout(function_box_layout)
        device_tab_layout.addWidget(function_box, 2, 0, 1, 2)

        function_box_layout.addWidget(QLabel("Statistic function options:"), 2, 0)
        statistic_function = QComboBox()
        statistic_function.addItem("Mean", self.multimeter.calculate_average_average)
        statistic_function.addItem("Maximum", self.multimeter.calculate_average_maximum)
        statistic_function.addItem("Minimum", self.multimeter.calculate_average_minimum)
        statistic_function.addItem("Peak to peak", self.multimeter.calculate_average_ptpeak)
        statistic_function.addItem("Measurement counts", self.multimeter.calculate_average_count)
        statistic_function.addItem("Reset", self.multimeter.calculate_average_clear)
        statistic_function.setCurrentIndex(-1)
        function_box_layout.addWidget(statistic_function, 2, 1)

        activate_statistic_function = QPushButton()
        activate_statistic_function.setText("Get")
        activate_statistic_function.clicked.connect(lambda: self.send_command(statistic_function.currentData()))
        function_box_layout.addWidget(activate_statistic_function, 2, 2)

        self.switch_tab_bar()

        self.multimeter_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.multimeter_tab, "HMC8012")

    def activate_calc_function(self):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.multimeter.toggle_calculate_function("OFF"))
            sender.setText("Activate")
            sender.isActivated = False
        else:
            self.send_command(self.multimeter.toggle_calculate_function)
            sender.setText("Disable")
            sender.isActivated = True

    def configure_temperature(self, unit, probe, sensor):
        # measure_temperature(self, probe_type='DEF', sensor_type='DEF', unit='C')
        kwargs = {}
        if unit is not None:
            kwargs.update({"unit": unit})
        if probe != '':
            kwargs.update({"probe_type": probe})
        if sensor != '':
            kwargs.update({"sensor_type": sensor})
        self.send_command(lambda: self.multimeter.measure_temperature(**kwargs))

    def set_mathematic_function(self, value):
        self.send_command(lambda: self.multimeter.set_calculate_function(value))

    def configure_multimeter_measurements(self, last, new):
        sender = self.sender()
        if not (new < 0):
            func = sender.itemData(new)
            user_input, was_success = self.get_user_input("Measurement range", "Enter desired range (AUTO if empty)")
            if was_success:
                if user_input.isspace() or not user_input:
                    self.send_command(func)
                else:
                    self.send_command(lambda: func(user_input))
            else:
                sender.blockSignals(True)
                sender.setCurrentIndex(last)
                sender.blockSignals(False)

    def get_user_input(self, title, label):
        text, ok = QInputDialog.getText(self, title, label)
        return text, ok

    def create_common_commands_list(self, device):
        cmds_list = {
            "*TST?": device.tst,
            "*RST": device.rst,
            "SYSTem:LOCal": device.local,
            "SYSTem:REMote": device.remote
        }
        cmds_box = QComboBox()
        cmds_box.addItems(cmds_list)
        cmds_box.setCurrentIndex(-1)

        cmds_button = QPushButton()
        cmds_button.setText("Apply")
        cmds_button.clicked.connect(lambda: self.send_common_command(cmds_box, cmds_list))
        return cmds_list, cmds_box, cmds_button

    def get_device_options(self):
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
