import pyvisa
import serial
from serial import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle
from QSwitchControl import SwitchControl
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from datetime import datetime

from multimeter_HMC8012 import DigitalMultimeterHMC8012
from powersupply_HMC804x import PowerSupplyHMC804x
from powersupply_lowNoise import PowerSupplyLowNoise

available_power_supplies = {
    "HMC8043": PowerSupplyHMC804x,
    "LowNoise": PowerSupplyLowNoise
}

available_multimeters = {
    "HMC8012": DigitalMultimeterHMC8012
}


# SpinBox Up/Down signals credit: https://stackoverflow.com/a/65226649/10768248
class SpinBox(QDoubleSpinBox):
    stepChanged = pyqtSignal()
    upClicked = pyqtSignal()
    downClicked = pyqtSignal()

    def stepBy(self, step):
        value = self.value()
        super(SpinBox, self).stepBy(step)
        if self.value() != value:
            self.stepChanged.emit()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)

        control = self.style().hitTestComplexControl(
            QStyle.CC_SpinBox, opt, event.pos(), self
        )
        if control == QStyle.SC_SpinBoxUp:
            if self.maximum() != self.value():
                self.upClicked.emit()
                self.setValue(self.value() + self.singleStep())
        elif control == QStyle.SC_SpinBoxDown:
            if self.minimum() != self.value():
                self.downClicked.emit()
                self.setValue(self.value() - self.singleStep())
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or \
                event.key() == Qt.Key_PageUp or event.key() == Qt.Key_PageDown:
            event.ignore()
        else:
            super().keyPressEvent(event)


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
        self.powersupply_output_area = None
        self.multimeter_output_area = None
        self.measuring_loop = None
        self.power_supply_tab = None
        self.multimeter_tab = None
        self.measurement_tab = None
        self.power_supply = None
        self.is_power_supply_connected = False
        self.multimeter = None
        self.is_multimeter_connected = False
        self.characteristics_button = None
        self.is_measurement_opened = False
        self.measured_multimeter = None
        self.measured_power_supply = None
        self.file_writer = None
        self.output_file = None

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + "QLabel, QPushButton, QComboBox, QTabWidget, "
                                                                "QDoubleSpinBox, QLineEdit, QSpinBox"
                                                                "{font-size: 11pt;"
                                                                "font-weight: 500;"
                                                                "font-family: Arial;}" +
                           "QGroupBox{font-size: 10pt;}")

        self.device_options = self.get_device_options()

        self.powersupply_button = None
        self.powersupply_menu = None
        self.multimeter_button = None
        self.multimeter_menu = None
        self.connect_section = self.make_connect_tab()
        self.tab_bar = self.make_tab_bar()

        self.setWindowTitle("Measure it")

        layout = QGridLayout()

        layout.addWidget(self.connect_section, 0, 0)
        layout.addWidget(self.tab_bar, 1, 0)

        self.setLayout(layout)

    def handle_error(self, error):
        errmsg = QMessageBox()
        errmsg.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + "QMessageBox {font-size: 11pt;"
                                                                  "font-weight: 500;}")
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

        device_layout.addWidget(QLabel("Characteristic measurement"), 2, 0, 1, 2)

        self.characteristics_button = QPushButton()
        self.characteristics_button.setText("Open")
        self.characteristics_button.clicked.connect(self.add_measurement_tab)
        device_layout.addWidget(self.characteristics_button, 2, 2)

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
            self.power_supply.close()
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
            self.multimeter.close()
            self.multimeter = None
            self.is_multimeter_connected = False
            self.multimeter_button.setText("Connect")
            self.tab_bar.removeTab(self.tab_bar.indexOf(self.multimeter_tab))
            self.multimeter_tab.close()
            self.multimeter_menu.setDisabled(False)
            self.switch_tab_bar()

    def add_measurement_tab(self):
        if self.is_measurement_opened is False:
            multimeter_address = self.device_options.get("HMC8012")
            if multimeter_address is None:
                self.handle_error("Multimeter not available!")
                return
            powersupply_address = self.device_options.get("HMC8043")
            if powersupply_address is None:
                self.handle_error("Power supply not available!")
                return
            self.measured_multimeter = available_multimeters["HMC8012"](multimeter_address)
            self.measured_power_supply = available_power_supplies["HMC8043"](powersupply_address)

            self.characteristics_button.setText("Close")
            self.measurement_tab = QWidget()
            self.measurement_tab.setAttribute(Qt.WA_DeleteOnClose)
            measurement_tab_layout = QGridLayout()

            measurement_box = QGroupBox("Measurement")
            measurement_box_layout = QGridLayout()
            channel_menu = QComboBox()
            channel_menu_options = ["Channel 1", "Channel 2", "Channel 3"]
            channel_menu.addItems(channel_menu_options)
            channel_menu.setItemData(0, "OUT1")
            channel_menu.setItemData(1, "OUT2")
            channel_menu.setItemData(2, "OUT3")
            measurement_box_layout.addWidget(channel_menu, 0, 0)

            measurement_box_layout.addWidget(QLabel("Voltage"), 1, 0)
            measurement_box_layout.addWidget(QLabel("From"), 1, 1)
            voltage_from_input = QDoubleSpinBox()
            voltage_from_input.setSuffix(" V")
            voltage_from_input.setMaximum(3.2050E+01)
            voltage_from_input.setDecimals(3)
            measurement_box_layout.addWidget(voltage_from_input, 1, 2)
            measurement_box_layout.addWidget(QLabel("To"), 1, 3)
            voltage_to_input = QDoubleSpinBox()
            voltage_to_input.setSuffix(" V")
            voltage_to_input.setMaximum(3.2050E+01)
            voltage_to_input.setDecimals(3)
            measurement_box_layout.addWidget(voltage_to_input, 1, 4)

            measurement_box_layout.addWidget(QLabel("Step"), 2, 0)
            step_input = QDoubleSpinBox()
            step_input.setSuffix(" V")
            step_input.setMaximum(3.2050E+01)
            step_input.setDecimals(3)
            measurement_box_layout.addWidget(step_input, 2, 2)
            measurement_box.setLayout(measurement_box_layout)
            measurement_tab_layout.addWidget(measurement_box, 0, 0, 1, 5)

            measurement_tab_layout.addWidget(QLabel("Time delay"), 1, 0)
            time_delay_input = QDoubleSpinBox()
            time_delay_input.setMinimum(1.2)
            time_delay_input.setSuffix(" s")
            measurement_tab_layout.addWidget(time_delay_input, 1, 1)

            start_button = QPushButton("Start")
            start_button.clicked.connect(lambda: self.measure_characteristic(channel_menu.currentData(),
                                                                             voltage_from_input.value(),
                                                                             voltage_to_input.value(),
                                                                             step_input.value(),
                                                                             time_delay_input.value()))
            measurement_tab_layout.addWidget(start_button, 1, 3)

            start_button = QPushButton("Stop")
            start_button.clicked.connect(lambda: self.finish_measure_characteristic())
            measurement_tab_layout.addWidget(start_button, 1, 4)

            self.measurement_tab.setLayout(measurement_tab_layout)
            self.tab_bar.addTab(self.measurement_tab, "Characteristic measurement")
            self.is_measurement_opened = True
        else:
            self.measured_multimeter.close()
            self.measured_power_supply.close()
            self.measured_multimeter = None
            self.measured_power_supply = None
            self.characteristics_button.setText("Open")
            self.tab_bar.removeTab(self.tab_bar.indexOf(self.measurement_tab))
            self.measurement_tab.close()
            self.is_measurement_opened = False
        self.switch_tab_bar()

    def finish_measure_characteristic(self):
        if self.measuring_loop is not None:
            if self.measuring_loop.event_source is not None:
                self.measuring_loop.event_source.stop()
                self.measuring_loop = None
                self.measured_power_supply.set_output_channel_state(0, "OUT1")
                self.measured_power_supply.set_output_channel_state(0, "OUT2")
                self.measured_power_supply.set_output_channel_state(0, "OUT3")
                if self.output_file:
                    if not self.output_file.closed:
                        self.output_file.close()

    def animate_plot(self, i, xs, ys, voltage_list, delay, channel, previous_channel):
        self.measured_power_supply.set_source_voltage_level_immediate_amplitude(voltage_list[i], channel)
        time.sleep(delay)
        measured_value = float(self.measured_multimeter.measure_current_ac()[2])

        xs.append(voltage_list[i])
        ys.append(measured_value)

        self.file_writer.writerow([voltage_list[i], measured_value])

        plt.cla()
        plt.plot(xs, ys)

        # plt.title('')
        plt.ylabel('Current (A)')
        plt.xlabel('Voltage (V)')
        if len(voltage_list) == (i+1):
            self.output_file.close()
            self.measured_power_supply.set_output_channel_state(0, channel)
            self.measured_power_supply.set_output_channel(previous_channel)
            self.measuring_loop = None

    def measure_characteristic(self, channel, voltage_from, voltage_to, step, delay):
        if step == 0:
            return
        previous_channel = self.measured_power_supply.get_output_channel()[2]
        self.measured_power_supply.set_output_channel_state(1, channel)
        frame_count = int((voltage_to * 1000 - voltage_from * 1000) / (step * 1000)) + 1
        current_voltage = voltage_from
        voltage_list = []
        for x in range(frame_count):
            voltage_list.append(round(current_voltage, 3))
            current_voltage += step
        plt.ion()
        fig = plt.figure()
        xs = []
        ys = []
        self.output_file = open('../measurement_from_'+datetime.now().strftime("%d.%m.%Y-%H.%M.%S")+'.csv', 'a',
                                newline='')
        self.file_writer = csv.writer(self.output_file)
        # interval=1000 * delay
        self.measuring_loop = FuncAnimation(fig, fargs=(xs, ys, voltage_list, delay, channel, previous_channel),
                                            init_func=lambda: None, repeat=False, blit=False, frames=frame_count,
                                            func=self.animate_plot)

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

    def send_command(self, func, caller):
        if func is not None:
            res = func()
            self.evaluate_method_call(res, caller)

    def send_common_command(self, device_common_commands, device_common_commands_list, caller):
        inst = device_common_commands.currentText()
        if inst != '':
            res = device_common_commands_list[inst]()
            self.evaluate_method_call(res, caller)

    def evaluate_method_call(self, res, caller):
        if res[0] is not True:
            self.handle_error(res[2])
        else:
            if res[1] == "Query":
                if caller == "ps":
                    self.powersupply_output_area.setText(res[2])
                else:
                    self.multimeter_output_area.setText(res[2])
            else:
                if caller == "ps":
                    self.powersupply_output_area.setText("write success")
                else:
                    self.multimeter_output_area.setText("write success")

    def add_LowNoise_tab(self):
        self.power_supply_tab = QWidget()
        self.power_supply_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()

        device_box = QGroupBox("Channel options")
        device_box_layout = QGridLayout()

        # first_fuse_switch.stateChanged.connect(
        #     lambda: self.change_fuse_state(first_fuse_switch.checkState(), "OUT1", channel_box.currentText()))
        # fuse_state_box_layout.addWidget(first_fuse_switch, 0, 2)

        channel_state_box = QGroupBox("State")
        channel_state_box_layout = QGridLayout()
        channel_state_box_layout.addWidget(QLabel("Channel 1"), 0, 0)
        first_channel_state = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                            animation_duration=100, checked=False, change_cursor=True)
        first_channel_state.stateChanged.connect(lambda: self.change_channel_state(first_channel_state.checkState(), 1))
        channel_state_box_layout.addWidget(first_channel_state, 0, 1)
        channel_state_box_layout.addWidget(QLabel("Channel 2"), 1, 0)
        second_channel_state = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                             animation_duration=100, checked=False, change_cursor=True)
        second_channel_state.stateChanged.connect(
            lambda: self.change_channel_state(second_channel_state.checkState(), 2))
        channel_state_box_layout.addWidget(second_channel_state, 1, 1)
        channel_state_box_layout.addWidget(QLabel("Channel 3"), 2, 0)
        third_channel_state = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                            animation_duration=100, checked=False, change_cursor=True)
        third_channel_state.stateChanged.connect(lambda: self.change_channel_state(third_channel_state.checkState(), 3))
        channel_state_box_layout.addWidget(third_channel_state, 2, 1)
        channel_state_box_layout.addWidget(QLabel("Channel 4"), 3, 0)
        fourth_channel_state = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                             animation_duration=100, checked=False, change_cursor=True)
        fourth_channel_state.stateChanged.connect(
            lambda: self.change_channel_state(fourth_channel_state.checkState(), 4))
        channel_state_box_layout.addWidget(fourth_channel_state, 3, 1)
        channel_state_box.setLayout(channel_state_box_layout)
        device_box_layout.addWidget(channel_state_box, 0, 0)

        channel_voltage_box = QGroupBox("Voltage level")
        channel_voltage_box_layout = QGridLayout()
        first_channel_voltage = QSpinBox()
        first_channel_voltage.setSuffix(" mV")
        first_channel_voltage.setMaximum(3500)
        first_channel_voltage.editingFinished.connect(
            lambda: self.power_supply.set_voltage_level(1, self.sender().value()))
        channel_voltage_box_layout.addWidget(first_channel_voltage, 0, 0)
        second_channel_voltage = QSpinBox()
        second_channel_voltage.setSuffix(" mV")
        second_channel_voltage.setMaximum(3500)
        second_channel_voltage.editingFinished.connect(
            lambda: self.power_supply.set_voltage_level(2, self.sender().value()))
        channel_voltage_box_layout.addWidget(second_channel_voltage, 1, 0)
        third_channel_voltage = QSpinBox()
        third_channel_voltage.setSuffix(" mV")
        third_channel_voltage.setMaximum(3500)
        third_channel_voltage.editingFinished.connect(
            lambda: self.power_supply.set_voltage_level(3, self.sender().value()))
        channel_voltage_box_layout.addWidget(third_channel_voltage, 2, 0)
        fourth_channel_voltage = QSpinBox()
        fourth_channel_voltage.setSuffix(" mV")
        fourth_channel_voltage.setMaximum(3500)
        fourth_channel_voltage.editingFinished.connect(
            lambda: self.power_supply.set_voltage_level(4, self.sender().value()))
        channel_voltage_box_layout.addWidget(fourth_channel_voltage, 3, 0)
        channel_voltage_box.setLayout(channel_voltage_box_layout)
        device_box_layout.addWidget(channel_voltage_box, 0, 1)

        device_box.setLayout(device_box_layout)
        device_tab_layout.addWidget(device_box, 0, 0)

        self.switch_tab_bar()

        self.power_supply_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.power_supply_tab, "LowNoise")

    def change_channel_state(self, state, channel):
        if state == Qt.Checked:
            self.power_supply.set_channel_state(channel, 'e')
        elif state == Qt.Unchecked:
            self.power_supply.set_channel_state(channel, 'd')

    def add_HMC8043_tab(self):
        self.power_supply_tab = QWidget()
        self.power_supply_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()

        output_box = QGroupBox("Output")
        output_box_layout = QGridLayout()
        self.powersupply_output_area = QLineEdit()
        self.powersupply_output_area.setReadOnly(True)
        output_box_layout.addWidget(self.powersupply_output_area, 0, 0)
        output_box.setLayout(output_box_layout)
        device_tab_layout.addWidget(output_box, 0, 0, 1, 2)

        common_command_box = QGroupBox("Common commands")
        common_command_box_layout = QGridLayout()
        HMC8043_common_commands_list, HMC8043_common_commands = self.create_common_commands_list(self.power_supply)

        common_commands_button = QPushButton()
        common_commands_button.setText("Apply")
        common_commands_button.clicked.connect(
            lambda: self.send_common_command(HMC8043_common_commands, HMC8043_common_commands_list, "ps"))

        common_command_box_layout.addWidget(HMC8043_common_commands, 0, 0)
        common_command_box_layout.addWidget(common_commands_button, 0, 1)
        common_command_box.setLayout(common_command_box_layout)
        device_tab_layout.addWidget(common_command_box, 1, 0, 1, 2)

        output_settings_box = QGroupBox("Output options")
        output_settings_box_layout = QGridLayout()

        channel_settings_box = QGroupBox("Channel options")
        channel_settings_box_layout = QGridLayout()
        channel_settings_box_layout.addWidget(QLabel("Selected channel:"), 0, 0)
        channel_box = QComboBox()
        channel_box.addItems(["OUT3", "OUT2", "OUT1"])
        channel_box.currentIndexChanged.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        channel_box.setCurrentIndex(2)
        channel_settings_box_layout.addWidget(channel_box, 0, 1, 1, 2)

        channel_state = QPushButton("State")
        channel_state.clicked.connect(lambda: self. send_command(lambda:
                                                                 self.power_supply.get_output_channel_state(), "ps"))
        channel_settings_box_layout.addWidget(channel_state, 1, 0)
        channel_activation = QPushButton("Activate")
        channel_activation.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.set_output_channel_state(1, channel_box.currentText()), "ps"))
        channel_settings_box_layout.addWidget(channel_activation, 1, 1)
        channel_deactivation = QPushButton("Deactivate")
        channel_deactivation.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.set_output_channel_state(0, channel_box.currentText()), "ps"))
        channel_settings_box_layout.addWidget(channel_deactivation, 1, 2)
        channel_settings_box.setLayout(channel_settings_box_layout)
        output_settings_box_layout.addWidget(channel_settings_box, 0, 0)

        master_settings_box = QGroupBox("Master options")
        master_settings_box_layout = QGridLayout()
        master_label = QLabel("Master output:")
        master_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        master_settings_box_layout.addWidget(master_label, 0, 0)
        master_state = QPushButton("State")
        master_state.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.get_output_master_state(), "ps"))
        master_settings_box_layout.addWidget(master_state, 0, 1)
        master_activation = QPushButton("Activate")
        master_activation.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.set_output_master_state(1, channel_box.currentText()), "ps"))
        master_settings_box_layout.addWidget(master_activation, 1, 0)
        master_deactivation = QPushButton("Deactivate")
        master_deactivation.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.set_output_master_state(0, channel_box.currentText()), "ps"))
        master_settings_box_layout.addWidget(master_deactivation, 1, 1)
        master_settings_box.setLayout(master_settings_box_layout)
        output_settings_box_layout.addWidget(master_settings_box, 1, 0)

        output_settings_box.setLayout(output_settings_box_layout)
        device_tab_layout.addWidget(output_settings_box, 3, 0, 2, 2)

        fuse_options_box = QGroupBox("Fuse options")
        fuse_options_box_layout = QGridLayout()
        fuse_state_box = QGroupBox()
        fuse_state_box_layout = QGridLayout()
        fuse_state_box_layout.addWidget(QLabel("Fuse 1", ), 0, 0)
        first_fuse_state_label = QLabel("State:")
        first_fuse_state_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fuse_state_box_layout.addWidget(first_fuse_state_label, 0, 1)
        first_fuse_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                          animation_duration=100, checked=False, change_cursor=True)
        first_fuse_switch.stateChanged.connect(
            lambda: self.change_fuse_state(first_fuse_switch.checkState(), "OUT1", channel_box.currentText()))
        fuse_state_box_layout.addWidget(first_fuse_switch, 0, 2)
        first_fuse_delay_button = QPushButton()
        first_fuse_delay_button.setText("Delay")
        first_fuse_delay_button.clicked.connect(lambda: self.set_fuse_delay(1, channel_box.currentText()))
        fuse_state_box_layout.addWidget(first_fuse_delay_button, 0, 3)
        first_fuse_trip_button = QPushButton()
        first_fuse_trip_button.setText("Trip")
        first_fuse_trip_button.clicked.connect(lambda: self.send_command(lambda:
                                                                         self.power_supply.fuse_trip("OUT1"), "ps"))
        first_fuse_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        fuse_state_box_layout.addWidget(first_fuse_trip_button, 0, 4)
        fuse_state_box_layout.addWidget(QLabel("Fuse 2", ), 1, 0)
        second_fuse_state_label = QLabel("State:")
        second_fuse_state_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fuse_state_box_layout.addWidget(second_fuse_state_label, 1, 1)
        second_fuse_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                           animation_duration=100, checked=False, change_cursor=True)
        second_fuse_switch.stateChanged.connect(
            lambda: self.change_fuse_state(second_fuse_switch.checkState(), "OUT2", channel_box.currentText()))
        fuse_state_box_layout.addWidget(second_fuse_switch, 1, 2)
        second_fuse_delay_button = QPushButton()
        second_fuse_delay_button.setText("Delay")
        second_fuse_delay_button.clicked.connect(lambda: self.set_fuse_delay(2, channel_box.currentText()))
        fuse_state_box_layout.addWidget(second_fuse_delay_button, 1, 3)
        second_fuse_trip_button = QPushButton()
        second_fuse_trip_button.setText("Trip")
        second_fuse_trip_button.clicked.connect(lambda: self.send_command(lambda:
                                                                          self.power_supply.fuse_trip("OUT2"), "ps"))
        second_fuse_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        fuse_state_box_layout.addWidget(second_fuse_trip_button, 1, 4)
        fuse_state_box_layout.addWidget(QLabel("Fuse 3", ), 2, 0)
        third_fuse_state_label = QLabel("State:")
        third_fuse_state_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fuse_state_box_layout.addWidget(third_fuse_state_label, 2, 1)
        third_fuse_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                          animation_duration=100, checked=False, change_cursor=True)
        third_fuse_switch.stateChanged.connect(
            lambda: self.change_fuse_state(third_fuse_switch.checkState(), "OUT3", channel_box.currentText()))
        fuse_state_box_layout.addWidget(third_fuse_switch, 2, 2)
        third_fuse_delay_button = QPushButton()
        third_fuse_delay_button.setText("Delay")
        third_fuse_delay_button.clicked.connect(lambda: self.set_fuse_delay(3, channel_box.currentText()))
        fuse_state_box_layout.addWidget(third_fuse_delay_button, 2, 3)
        third_fuse_trip_button = QPushButton()
        third_fuse_trip_button.setText("Trip")
        third_fuse_trip_button.clicked.connect(lambda: self.send_command(lambda:
                                                                         self.power_supply.fuse_trip("OUT3"), "ps"))
        third_fuse_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        fuse_state_box_layout.addWidget(third_fuse_trip_button, 2, 4)
        fuse_state_box.setLayout(fuse_state_box_layout)
        fuse_options_box_layout.addWidget(fuse_state_box, 0, 0)

        fuse_linking_box = QGroupBox("Link && unlink fuses")
        fuse_linking_box_layout = QGridLayout()
        fuse_linking_box_layout.addWidget(QLabel("Fuse CH1 with fuse CH2"), 0, 0)
        first_fuse_link_button = ButtonWithSwitch()
        first_fuse_link_button.setText("Link")
        first_fuse_link_button.clicked.connect(lambda: self.link_unlink_fuse(2, "OUT1", channel_box.currentText()))
        fuse_linking_box_layout.addWidget(first_fuse_link_button, 0, 1)
        fuse_linking_box_layout.addWidget(QLabel("Fuse CH2 with fuse CH3"), 1, 0)
        second_fuse_link_button = ButtonWithSwitch()
        second_fuse_link_button.setText("Link")
        second_fuse_link_button.clicked.connect(lambda: self.link_unlink_fuse(3, "OUT2", channel_box.currentText()))
        fuse_linking_box_layout.addWidget(second_fuse_link_button, 1, 1)
        fuse_linking_box_layout.addWidget(QLabel("Fuse CH3 with fuse CH1"), 2, 0)
        third_fuse_link_button = ButtonWithSwitch()
        third_fuse_link_button.setText("Link")
        third_fuse_link_button.clicked.connect(lambda: self.link_unlink_fuse(1, "OUT3", channel_box.currentText()))
        fuse_linking_box_layout.addWidget(third_fuse_link_button, 2, 1)
        fuse_linking_box.setLayout(fuse_linking_box_layout)
        fuse_options_box_layout.addWidget(fuse_linking_box, 1, 0)

        fuse_options_box.setLayout(fuse_options_box_layout)
        device_tab_layout.addWidget(fuse_options_box, 1, 4, 2, 2)

        measurement_options_box = QGroupBox("Measurement options")
        measurement_options_box_layout = QGridLayout()
        measurement_options_box_layout.addWidget(QLabel("Value to measure:"), 0, 0)
        measurement_box = QComboBox()
        measurement_box.addItem("Current", self.power_supply.measure_scalar_current_dc)
        measurement_box.addItem("Voltage", self.power_supply.measure_scalar_voltage_dc)
        measurement_box.addItem("Power", self.power_supply.measure_scalar_power)
        measurement_box.addItem("Current released energy", self.power_supply.measure_scalar_energy)
        measurement_options_box_layout.addWidget(measurement_box, 0, 1)
        measure_selected_value = ButtonWithSwitch()
        measure_selected_value.setText("Query")
        measure_selected_value.clicked.connect(
            lambda: self.send_command(lambda: measurement_box.currentData()(channel_box.currentText()), "ps"))
        measurement_options_box_layout.addWidget(measure_selected_value, 0, 2)
        measurement_options_box.setLayout(measurement_options_box_layout)
        device_tab_layout.addWidget(measurement_options_box, 2, 0, 1, 2)

        ainput_ramp_box = QGroupBox("Analog In && EasyRamp")
        ainput_ramp_layout = QGridLayout()

        ainput_box = QGroupBox("Analog In options")
        ainput_layout = QGridLayout()
        input_unit_label = QLabel("In unit:")
        # input_unit_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ainput_layout.addWidget(input_unit_label, 0, 0)
        ainput_unit = QComboBox()
        ainput_unit.addItem("Voltage", "VOLT")
        ainput_unit.addItem("Current", "CURR")
        ainput_layout.addWidget(ainput_unit, 0, 1)
        input_mode_label = QLabel("In mode:")
        ainput_layout.addWidget(input_mode_label, 0, 2)
        ainput_mode = QComboBox()
        ainput_mode.addItem("Linear", "LIN")
        ainput_mode.addItem("Step", "STEP")
        ainput_layout.addWidget(ainput_mode, 0, 4)
        ainput_layout.addWidget(QLabel("CH1:"), 1, 0)
        first_channel_ainput_state = ButtonWithSwitch()
        first_channel_ainput_state.setText("Activate")
        ainput_layout.addWidget(first_channel_ainput_state, 1, 1, 1, 4)
        first_channel_ainput_state.clicked.connect(lambda: self.send_command(self.setup_channel_ainput(
            ainput_unit.itemData(ainput_unit.currentIndex()), ainput_mode.itemData(ainput_mode.currentIndex()),
            "OUT1", channel_box.currentText()), "ps"))

        ainput_layout.addWidget(QLabel("CH2:"), 2, 0)
        second_channel_ainput_state = ButtonWithSwitch()
        second_channel_ainput_state.setText("Activate")
        ainput_layout.addWidget(second_channel_ainput_state, 2, 1, 1, 4)
        second_channel_ainput_state.clicked.connect(lambda: self.send_command(self.setup_channel_ainput(
            ainput_unit.itemData(ainput_unit.currentIndex()), ainput_mode.itemData(ainput_mode.currentIndex()),
            "OUT2", channel_box.currentText()), "ps"))

        ainput_layout.addWidget(QLabel("CH3:"), 3, 0)
        third_channel_ainput_state = ButtonWithSwitch()
        third_channel_ainput_state.setText("Activate")
        ainput_layout.addWidget(third_channel_ainput_state, 3, 1, 1, 4)
        third_channel_ainput_state.clicked.connect(lambda: self.send_command(self.setup_channel_ainput(
            ainput_unit.itemData(ainput_unit.currentIndex()), ainput_mode.itemData(ainput_mode.currentIndex()),
            "OUT3", channel_box.currentText()), "ps"))

        ainput_box.setLayout(ainput_layout)
        ainput_ramp_layout.addWidget(ainput_box, 0, 0)

        easyramp_box = QGroupBox("EasyRamp options")
        easyramp_layout = QGridLayout()
        ramp_duration_label = QLabel("Ramp duration:")
        easyramp_layout.addWidget(ramp_duration_label, 0, 0)
        easyramp_duration = QDoubleSpinBox()
        easyramp_duration.setMinimum(1.00E-02)
        easyramp_duration.setMaximum(1.000E+01)
        easyramp_duration.editingFinished.connect(lambda: self.send_command(
            lambda: self.power_supply.set_source_voltage_ramp_duration(easyramp_duration.value()), "ps"))
        easyramp_layout.addWidget(easyramp_duration, 0, 1)

        first_channel_easyramp_state = ButtonWithSwitch()
        first_channel_easyramp_state.setText("Activate")
        easyramp_layout.addWidget(first_channel_easyramp_state, 1, 0, 1, 2)
        first_channel_easyramp_state.clicked.connect(lambda: self.send_command(
            self.set_easyramp_state("OUT1", channel_box.currentText()), "ps"))

        second_channel_easyramp_state = ButtonWithSwitch()
        second_channel_easyramp_state.setText("Activate")
        easyramp_layout.addWidget(second_channel_easyramp_state, 2, 0, 1, 2)
        second_channel_easyramp_state.clicked.connect(lambda: self.send_command(
            self.set_easyramp_state("OUT2", channel_box.currentText()), "ps"))

        third_channel_easyramp_state = ButtonWithSwitch()
        third_channel_easyramp_state.setText("Activate")
        easyramp_layout.addWidget(third_channel_easyramp_state, 3, 0, 1, 2)
        third_channel_easyramp_state.clicked.connect(lambda: self.send_command(
            self.set_easyramp_state("OUT3", channel_box.currentText()), "ps"))

        easyramp_box.setLayout(easyramp_layout)
        ainput_ramp_layout.addWidget(easyramp_box, 0, 1)

        ainput_ramp_box.setLayout(ainput_ramp_layout)
        device_tab_layout.addWidget(ainput_ramp_box, 0, 2, 2, 2)

        voltage_box = QGroupBox("Voltage options")
        voltage_layout = QGridLayout()
        voltage_layout.addWidget(QLabel("Channel 1      Voltage:"), 0, 0)
        first_channel_voltage_value = SpinBox()
        first_channel_voltage_value.setRange(0, 3.2050E+01)
        first_channel_voltage_value.setDecimals(3)
        first_channel_voltage_value.setValue(0)
        first_channel_voltage_value.editingFinished.connect(
            lambda: self.change_channel_voltage("OUT1", channel_box.currentText()))
        first_channel_voltage_value.upClicked.connect(
            lambda: self.increase_channel_voltage("OUT1", channel_box.currentText()))
        first_channel_voltage_value.downClicked.connect(
            lambda: self.decrease_channel_voltage("OUT1", channel_box.currentText()))
        voltage_layout.addWidget(first_channel_voltage_value, 0, 1)

        voltage_layout.addWidget(QLabel("Channel 2      Voltage:"), 1, 0)
        second_channel_voltage_value = SpinBox()
        second_channel_voltage_value.setRange(0, 3.2050E+01)
        second_channel_voltage_value.setDecimals(3)
        second_channel_voltage_value.setValue(0)
        second_channel_voltage_value.editingFinished.connect(
            lambda: self.change_channel_voltage("OUT2", channel_box.currentText()))
        second_channel_voltage_value.upClicked.connect(
            lambda: self.increase_channel_voltage("OUT2", channel_box.currentText()))
        second_channel_voltage_value.downClicked.connect(
            lambda: self.decrease_channel_voltage("OUT2", channel_box.currentText()))
        voltage_layout.addWidget(second_channel_voltage_value, 1, 1)

        voltage_layout.addWidget(QLabel("Channel 3      Voltage:"), 2, 0)
        third_channel_voltage_value = SpinBox()
        third_channel_voltage_value.setRange(0, 3.2050E+01)
        third_channel_voltage_value.setDecimals(3)
        third_channel_voltage_value.setValue(0)
        third_channel_voltage_value.editingFinished.connect(
            lambda: self.change_channel_voltage("OUT3", channel_box.currentText()))
        third_channel_voltage_value.upClicked.connect(
            lambda: self.increase_channel_voltage("OUT3", channel_box.currentText()))
        third_channel_voltage_value.downClicked.connect(
            lambda: self.decrease_channel_voltage("OUT3", channel_box.currentText()))
        voltage_layout.addWidget(third_channel_voltage_value, 2, 1)

        voltage_layout.addWidget(QLabel("Voltage step size:"), 0, 2, 3, 1)
        channel_voltage_step = SpinBox()
        channel_voltage_step.setRange(0, 3.2050E+01)
        channel_voltage_step.setDecimals(3)
        channel_voltage_step.setValue(1)
        channel_voltage_step.editingFinished.connect(lambda: first_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.editingFinished.connect(lambda: second_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.editingFinished.connect(lambda: third_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.editingFinished.connect(self.volt_step_changed)
        channel_voltage_step.stepChanged.connect(lambda: first_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.stepChanged.connect(lambda: second_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.stepChanged.connect(lambda: third_channel_voltage_value.setSingleStep(
            channel_voltage_step.value()))
        channel_voltage_step.stepChanged.connect(self.volt_step_changed)
        voltage_layout.addWidget(channel_voltage_step, 0, 4, 3, 1)
        voltage_box.setLayout(voltage_layout)
        device_tab_layout.addWidget(voltage_box, 3, 4, 1, 2)

        current_box = QGroupBox("Current options")
        current_layout = QGridLayout()
        current_layout.addWidget(QLabel("Channel 1      Current:"), 0, 0)
        first_channel_current_value = SpinBox()
        first_channel_current_value.setRange(0.0005, 3.0000)
        first_channel_current_value.setDecimals(4)
        first_channel_current_value.setValue(0.0005)
        first_channel_current_value.setSingleStep(1.0000E-01)
        first_channel_current_value.editingFinished.connect(
            lambda: self.change_channel_current("OUT1", channel_box.currentText()))
        first_channel_current_value.upClicked.connect(
            lambda: self.increase_channel_current("OUT1", channel_box.currentText()))
        first_channel_current_value.downClicked.connect(
            lambda: self.decrease_channel_current("OUT1", channel_box.currentText()))
        current_layout.addWidget(first_channel_current_value, 0, 1)

        current_layout.addWidget(QLabel("Channel 2      Current:"), 1, 0)
        second_channel_current_value = SpinBox()
        second_channel_current_value.setRange(0.0005, 3.0000)
        second_channel_current_value.setDecimals(4)
        second_channel_current_value.setValue(0.0005)
        second_channel_current_value.setSingleStep(1.0000E-01)
        second_channel_current_value.editingFinished.connect(
            lambda: self.change_channel_current("OUT2", channel_box.currentText()))
        second_channel_current_value.upClicked.connect(
            lambda: self.increase_channel_current("OUT2", channel_box.currentText()))
        second_channel_current_value.downClicked.connect(
            lambda: self.decrease_channel_current("OUT2", channel_box.currentText()))
        current_layout.addWidget(second_channel_current_value, 1, 1)

        current_layout.addWidget(QLabel("Channel 3      Current:"), 2, 0)
        third_channel_current_value = SpinBox()
        third_channel_current_value.setRange(0.0005, 3.0000)
        third_channel_current_value.setDecimals(4)
        third_channel_current_value.setValue(0.0005)
        third_channel_current_value.setSingleStep(1.0000E-01)
        third_channel_current_value.editingFinished.connect(
            lambda: self.change_channel_current("OUT3", channel_box.currentText()))
        third_channel_current_value.upClicked.connect(
            lambda: self.increase_channel_current("OUT3", channel_box.currentText()))
        third_channel_current_value.downClicked.connect(
            lambda: self.decrease_channel_current("OUT3", channel_box.currentText()))
        current_layout.addWidget(third_channel_current_value, 2, 1)

        current_layout.addWidget(QLabel("Current step size:"), 0, 2, 3, 1)
        channel_current_step = SpinBox()
        channel_current_step.setRange(5.0000E-04, 3.000E+00)
        channel_current_step.setDecimals(4)
        channel_current_step.setValue(1.0000E-01)
        channel_current_step.editingFinished.connect(lambda: first_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.editingFinished.connect(lambda: second_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.editingFinished.connect(lambda: third_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.editingFinished.connect(self.curr_step_changed)
        channel_current_step.stepChanged.connect(lambda: first_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.stepChanged.connect(lambda: second_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.stepChanged.connect(lambda: third_channel_current_value.setSingleStep(
            channel_current_step.value()))
        channel_current_step.stepChanged.connect(self.curr_step_changed)
        current_layout.addWidget(channel_current_step, 0, 4, 3, 1)
        current_box.setLayout(current_layout)
        device_tab_layout.addWidget(current_box, 4, 4, 1, 2)

        protection_options_box = QGroupBox("Protection options")
        protection_options_box_layout = QGridLayout()
        ovp_box = QGroupBox("OVP settings")
        ovp_layout = QGridLayout()
        ovp_layout.addWidget(QLabel("CH1 OVP value:"), 0, 0)
        first_channel_ovp_value = QDoubleSpinBox()
        first_channel_ovp_value.setValue(3.2050E+01)
        first_channel_ovp_value.setRange(0, 3.2050E+01)
        first_channel_ovp_value.setDecimals(3)
        first_channel_ovp_value.setSingleStep(1.0000E-03)
        first_channel_ovp_value.valueChanged.connect(lambda: self.send_command(
            self.change_ovp_value("OUT1", channel_box.currentText()), "ps"))
        ovp_layout.addWidget(first_channel_ovp_value, 0, 1)
        ovp_layout.addWidget(QLabel("Mode:"), 0, 2)
        first_channel_ovp_mode = QComboBox()
        first_channel_ovp_mode.addItem("Measured", "MEAS")
        first_channel_ovp_mode.addItem("Protected", "PROT")
        first_channel_ovp_mode.setCurrentIndex(-1)
        first_channel_ovp_mode.currentIndexChanged.connect(
            lambda: self.change_ovp_mode("OUT1", channel_box.currentText()))
        ovp_layout.addWidget(first_channel_ovp_mode, 0, 3)
        first_ovp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                         animation_duration=100, checked=False, change_cursor=True)
        first_ovp_switch.stateChanged.connect(
            lambda: self.change_ovp_state("OUT1", channel_box.currentText()))
        ovp_layout.addWidget(first_ovp_switch, 0, 4)
        first_ovp_trip_button = QPushButton()
        first_ovp_trip_button.setText("Trip")
        first_ovp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_trip("OUT1"), "ps"))
        first_ovp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(first_ovp_trip_button, 0, 5)
        first_ovp_clear_button = QPushButton()
        first_ovp_clear_button.setText("Clear")
        first_ovp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_clear("OUT1"), "ps"))
        first_ovp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(first_ovp_clear_button, 0, 6)

        ovp_layout.addWidget(QLabel("CH2 OVP value:"), 1, 0)
        second_channel_ovp_value = QDoubleSpinBox()
        second_channel_ovp_value.setValue(3.2050E+01)
        second_channel_ovp_value.setRange(0, 3.2050E+01)
        second_channel_ovp_value.setDecimals(3)
        second_channel_ovp_value.setSingleStep(1.0000E-03)
        second_channel_ovp_value.valueChanged.connect(lambda: self.send_command(
            self.change_ovp_value("OUT2", channel_box.currentText()), "ps"))
        ovp_layout.addWidget(second_channel_ovp_value, 1, 1)
        ovp_layout.addWidget(QLabel("Mode:"), 1, 2)
        second_channel_ovp_mode = QComboBox()
        second_channel_ovp_mode.addItem("Measured", "MEAS")
        second_channel_ovp_mode.addItem("Protected", "PROT")
        second_channel_ovp_mode.setCurrentIndex(-1)
        second_channel_ovp_mode.currentIndexChanged.connect(
            lambda: self.change_ovp_mode("OUT2", channel_box.currentText()))
        ovp_layout.addWidget(second_channel_ovp_mode, 1, 3)
        second_ovp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                          animation_duration=100, checked=False, change_cursor=True)
        second_ovp_switch.stateChanged.connect(
            lambda: self.change_ovp_state("OUT2", channel_box.currentText()))
        ovp_layout.addWidget(second_ovp_switch, 1, 4)
        second_ovp_trip_button = QPushButton()
        second_ovp_trip_button.setText("Trip")
        second_ovp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_trip("OUT2"), "ps"))
        second_ovp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(second_ovp_trip_button, 1, 5)
        second_ovp_clear_button = QPushButton()
        second_ovp_clear_button.setText("Clear")
        second_ovp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_clear("OUT2"), "ps"))
        second_ovp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(second_ovp_clear_button, 1, 6)

        ovp_layout.addWidget(QLabel("CH3 OVP value:"), 2, 0)
        third_channel_ovp_value = QDoubleSpinBox()
        third_channel_ovp_value.setValue(3.2050E+01)
        third_channel_ovp_value.setRange(0, 3.2050E+01)
        third_channel_ovp_value.setDecimals(3)
        third_channel_ovp_value.setSingleStep(1.0000E-03)
        third_channel_ovp_value.valueChanged.connect(lambda: self.send_command(
            self.change_ovp_value("OUT3", channel_box.currentText()), "ps"))
        ovp_layout.addWidget(third_channel_ovp_value, 2, 1)
        ovp_layout.addWidget(QLabel("Mode:"), 2, 2)
        third_channel_ovp_mode = QComboBox()
        third_channel_ovp_mode.addItem("Measured", "MEAS")
        third_channel_ovp_mode.addItem("Protected", "PROT")
        third_channel_ovp_mode.setCurrentIndex(-1)
        third_channel_ovp_mode.currentIndexChanged.connect(
            lambda: self.change_ovp_mode("OUT3", channel_box.currentText()))
        ovp_layout.addWidget(third_channel_ovp_mode, 2, 3)
        third_ovp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                         animation_duration=100, checked=False, change_cursor=True)
        third_ovp_switch.stateChanged.connect(
            lambda: self.change_ovp_state("OUT3", channel_box.currentText()))
        ovp_layout.addWidget(third_ovp_switch, 2, 4)
        third_ovp_trip_button = QPushButton()
        third_ovp_trip_button.setText("Trip")
        third_ovp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_trip("OUT3"), "ps"))
        third_ovp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(third_ovp_trip_button, 2, 5)
        third_ovp_clear_button = QPushButton()
        third_ovp_clear_button.setText("Clear")
        third_ovp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_voltage_protection_clear("OUT3"), "ps"))
        third_ovp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        ovp_layout.addWidget(third_ovp_clear_button, 2, 6)

        ovp_box.setLayout(ovp_layout)

        opp_box = QGroupBox("OPP settings")
        opp_layout = QGridLayout()
        opp_layout.addWidget(QLabel("CH1 OPP value:"), 0, 0)
        first_channel_opp_value = QDoubleSpinBox()
        first_channel_opp_value.setValue(3.300E+01)
        first_channel_opp_value.setRange(0, 3.300E+01)
        first_channel_opp_value.setDecimals(2)
        first_channel_opp_value.setSingleStep(1.0000E-02)
        first_channel_opp_value.valueChanged.connect(lambda: self.send_command(
            self.change_opp_value("OUT1", channel_box.currentText()), "ps"))
        opp_layout.addWidget(first_channel_opp_value, 0, 1)
        first_opp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                         animation_duration=100, checked=False, change_cursor=True)
        first_opp_switch.stateChanged.connect(
            lambda: self.change_opp_state("OUT1", channel_box.currentText()))
        opp_layout.addWidget(first_opp_switch, 0, 2)
        first_opp_trip_button = QPushButton()
        first_opp_trip_button.setText("Trip")
        first_opp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_trip("OUT1"), "ps"))
        first_opp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(first_opp_trip_button, 0, 3)
        first_opp_clear_button = QPushButton()
        first_opp_clear_button.setText("Clear")
        first_opp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_clear("OUT1"), "ps"))
        first_opp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(first_opp_clear_button, 0, 4)

        opp_layout.addWidget(QLabel("CH2 OPP value:"), 1, 0)
        second_channel_opp_value = QDoubleSpinBox()
        second_channel_opp_value.setValue(3.300E+01)
        second_channel_opp_value.setRange(0, 3.300E+01)
        second_channel_opp_value.setDecimals(2)
        second_channel_opp_value.setSingleStep(1.0000E-02)
        second_channel_opp_value.valueChanged.connect(lambda: self.send_command(
            self.change_opp_value("OUT2", channel_box.currentText()), "ps"))
        opp_layout.addWidget(second_channel_opp_value, 1, 1)
        second_opp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                          animation_duration=100, checked=False, change_cursor=True)
        second_opp_switch.stateChanged.connect(
            lambda: self.change_opp_state("OUT2", channel_box.currentText()))
        opp_layout.addWidget(second_opp_switch, 1, 2)
        second_opp_trip_button = QPushButton()
        second_opp_trip_button.setText("Trip")
        second_opp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_trip("OUT2"), "ps"))
        second_opp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(second_opp_trip_button, 1, 3)
        second_opp_clear_button = QPushButton()
        second_opp_clear_button.setText("Clear")
        second_opp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_clear("OUT2"), "ps"))
        second_opp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(second_opp_clear_button, 1, 4)

        opp_layout.addWidget(QLabel("CH3 OPP value:"), 2, 0)
        third_channel_opp_value = QDoubleSpinBox()
        third_channel_opp_value.setValue(3.300E+01)
        third_channel_opp_value.setRange(0, 3.300E+01)
        third_channel_opp_value.setDecimals(2)
        third_channel_opp_value.setSingleStep(1.0000E-02)
        third_channel_opp_value.valueChanged.connect(lambda: self.send_command(
            self.change_opp_value("OUT3", channel_box.currentText()), "ps"))
        opp_layout.addWidget(third_channel_opp_value, 2, 1)
        third_opp_switch = SwitchControl(bg_color="#455364", circle_color="#DDD", active_color="#259adf",
                                         animation_duration=100, checked=False, change_cursor=True)
        third_opp_switch.stateChanged.connect(
            lambda: self.change_opp_state("OUT3", channel_box.currentText()))
        opp_layout.addWidget(third_opp_switch, 2, 2)
        third_opp_trip_button = QPushButton()
        third_opp_trip_button.setText("Trip")
        third_opp_trip_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_trip("OUT3"), "ps"))
        third_opp_trip_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(third_opp_trip_button, 2, 3)
        third_opp_clear_button = QPushButton()
        third_opp_clear_button.setText("Clear")
        third_opp_clear_button.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.source_power_protection_clear("OUT3"), "ps"))
        third_opp_clear_button.clicked.connect(lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        opp_layout.addWidget(third_opp_clear_button, 2, 4)

        opp_box.setLayout(opp_layout)

        protection_options_box_layout.addWidget(ovp_box, 0, 0)
        protection_options_box_layout.addWidget(opp_box, 1, 0)
        protection_options_box.setLayout(protection_options_box_layout)
        device_tab_layout.addWidget(protection_options_box, 3, 2, 2, 2)

        energy_meter_box = QGroupBox("Energy meter options")
        energy_meter_layout = QGridLayout()

        energy_meter_layout.addWidget(QLabel("Channel 1 energy meter:"), 0, 0)
        first_channel_energy_meter_state = ButtonWithSwitch()
        first_channel_energy_meter_state.setText("Activate")
        energy_meter_layout.addWidget(first_channel_energy_meter_state, 0, 1)
        first_channel_energy_meter_state.clicked.connect(lambda: self.send_command(
            self.set_energy_meter_state("OUT1", channel_box.currentText()), "ps"))

        first_channel_energy_meter_reset = QPushButton()
        first_channel_energy_meter_reset.setText("Reset")
        first_channel_energy_meter_reset.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.measure_scalar_energy_reset("OUT1"), "ps"))
        first_channel_energy_meter_reset.clicked.connect(
            lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        energy_meter_layout.addWidget(first_channel_energy_meter_reset, 0, 2)

        energy_meter_layout.addWidget(QLabel("Channel 2 energy meter:"), 1, 0)
        second_channel_energy_meter_state = ButtonWithSwitch()
        second_channel_energy_meter_state.setText("Activate")
        energy_meter_layout.addWidget(second_channel_energy_meter_state, 1, 1)
        second_channel_energy_meter_state.clicked.connect(lambda: self.send_command(
            self.set_energy_meter_state("OUT2", channel_box.currentText()), "ps"))

        second_channel_energy_meter_reset = QPushButton()
        second_channel_energy_meter_reset.setText("Reset")
        second_channel_energy_meter_reset.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.measure_scalar_energy_reset("OUT2"), "ps"))
        second_channel_energy_meter_reset.clicked.connect(
            lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        energy_meter_layout.addWidget(second_channel_energy_meter_reset, 1, 2)

        energy_meter_layout.addWidget(QLabel("Channel 3 energy meter:"), 2, 0)
        third_channel_energy_meter_state = ButtonWithSwitch()
        third_channel_energy_meter_state.setText("Activate")
        energy_meter_layout.addWidget(third_channel_energy_meter_state, 2, 1)
        third_channel_energy_meter_state.clicked.connect(lambda: self.send_command(
            self.set_energy_meter_state("OUT3", channel_box.currentText()), "ps"))

        third_channel_energy_meter_reset = QPushButton()
        third_channel_energy_meter_reset.setText("Reset")
        third_channel_energy_meter_reset.clicked.connect(lambda: self.send_command(
            lambda: self.power_supply.measure_scalar_energy_reset("OUT3"), "ps"))
        third_channel_energy_meter_reset.clicked.connect(
            lambda: self.power_supply.set_output_channel(channel_box.currentText()))
        energy_meter_layout.addWidget(third_channel_energy_meter_reset, 2, 2)

        energy_meter_box.setLayout(energy_meter_layout)
        device_tab_layout.addWidget(energy_meter_box, 0, 4, 1, 2)

        self.switch_tab_bar()

        self.power_supply_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.power_supply_tab, "HMC8043")

    def set_energy_meter_state(self, affected_channel, selected_channel):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.power_supply.set_measure_scalar_energy_state(0, affected_channel), "ps")
            sender.setText("Activate")
            sender.isActivated = False
        else:
            self.send_command(lambda: self.power_supply.set_measure_scalar_energy_state(1, affected_channel), "ps")
            sender.setText("Deactivate")
            sender.isActivated = True
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def set_easyramp_state(self, affected_channel, selected_channel):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.power_supply.set_source_voltage_ramp_state(0, affected_channel), "ps")
            sender.setText("Activate")
            sender.isActivated = False
        else:
            self.send_command(lambda: self.power_supply.set_source_voltage_ramp_state(1, affected_channel), "ps")
            sender.setText("Deactivate")
            sender.isActivated = True
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def setup_channel_ainput(self, ainput_unit, ainput_mode, affected_channel, selected_channel):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.power_supply.set_source_voltage_ainput_state(0, affected_channel), "ps")
            sender.setText("Activate")
            sender.isActivated = False
        else:
            if ainput_mode == "STEP":
                user_input, was_success = self.get_user_input(
                    "STEP threshold", "Set the threshold for the Analog In mode STEP of channel "
                                      + affected_channel + "(0V to 10V)")
                if was_success:
                    self.send_command(lambda: self.power_supply.set_source_voltage_ainput_mode(ainput_mode), "ps")
                    self.send_command(lambda: self.power_supply.set_source_voltage_ainput_input(ainput_unit), "ps")
                    self.send_command(lambda: self.power_supply.set_source_voltage_ainput_threshold(user_input), "ps")
                    self.send_command(lambda:
                                      self.power_supply.set_source_voltage_ainput_state(1, affected_channel), "ps")
                    sender.setText("Deactivate")
                    sender.isActivated = True
            else:
                self.send_command(lambda: self.power_supply.set_source_voltage_ainput_mode(ainput_mode), "ps")
                self.send_command(lambda: self.power_supply.set_source_voltage_ainput_input(ainput_unit), "ps")
                self.send_command(lambda: self.power_supply.set_source_voltage_ainput_state(1, affected_channel), "ps")
                sender.setText("Deactivate")
                sender.isActivated = True
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_ovp_mode(self, affected_channel, selected_channel):
        self.send_command(lambda: self.power_supply.set_source_voltage_protection_mode(
            self.sender().itemData(self.sender().currentIndex()), affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_opp_state(self, affected_channel, selected_channel):
        state = self.sender().checkState()
        if state == Qt.Checked:
            self.send_command(lambda: self.power_supply.set_source_power_protection_state(1, affected_channel), "ps")
        elif state == Qt.Unchecked:
            self.send_command(lambda: self.power_supply.set_source_power_protection_state(0, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_opp_value(self, affected_channel, selected_channel):
        pow_value = round(self.sender().value(), 2)
        self.send_command(
            lambda: self.power_supply.set_source_power_protection_level(pow_value, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_ovp_state(self, affected_channel, selected_channel):
        state = self.sender().checkState()
        if state == Qt.Checked:
            self.send_command(lambda: self.power_supply.set_source_voltage_protection_state(1, affected_channel), "ps")
        elif state == Qt.Unchecked:
            self.send_command(lambda: self.power_supply.set_source_voltage_protection_state(0, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_ovp_value(self, affected_channel, selected_channel):
        volt_value = round(self.sender().value(), 3)
        self.send_command(
            lambda: self.power_supply.set_source_voltage_protection_level(volt_value, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_channel_voltage(self, affected_channel, selected_channel):
        voltage = round(self.sender().value(), 3)
        self.send_command(
            lambda: self.power_supply.set_source_voltage_level_immediate_amplitude(voltage, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def increase_channel_voltage(self, affected_channel, selected_channel):
        self.send_command(
            lambda: self.power_supply.vary_source_voltage_level_immediate_amplitude("UP", affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def decrease_channel_voltage(self, affected_channel, selected_channel):
        self.send_command(
            lambda: self.power_supply.vary_source_voltage_level_immediate_amplitude("DOWN", affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def volt_step_changed(self):
        step = round(self.sender().value(), 3)
        self.send_command(lambda: self.power_supply.set_source_voltage_level_step_increment(step), "ps")

    def change_channel_current(self, affected_channel, selected_channel):
        current = round(self.sender().value(), 4)
        self.send_command(
            lambda: self.power_supply.set_source_current_level_immediate_amplitude(current, affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def increase_channel_current(self, affected_channel, selected_channel):
        self.send_command(
            lambda: self.power_supply.vary_source_current_level_immediate_amplitude("UP", affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def decrease_channel_current(self, affected_channel, selected_channel):
        self.send_command(
            lambda: self.power_supply.vary_source_current_level_immediate_amplitude("DOWN", affected_channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def curr_step_changed(self):
        step = round(self.sender().value(), 4)
        self.send_command(lambda: self.power_supply.set_source_current_level_step_increment(step), "ps")

    def link_unlink_fuse(self, fuse_to_link, fuse_to_be_linked, selected_channel):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.power_supply.set_output_channel(fuse_to_be_linked), "ps")
            self.send_command(lambda: self.power_supply.fuse_unlink(fuse_to_link), "ps")
            sender.setText("Link")
            sender.isActivated = False
        else:
            self.send_command(lambda: self.power_supply.set_fuse_link(fuse_to_link, fuse_to_be_linked), "ps")
            sender.setText("Unlink")
            sender.isActivated = True
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def change_fuse_state(self, state, channel, selected_channel):
        if state == Qt.Checked:
            self.send_command(lambda: self.power_supply.set_fuse_state(1, channel), "ps")
        elif state == Qt.Unchecked:
            self.send_command(lambda: self.power_supply.set_fuse_state(0, channel), "ps")
        self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def set_fuse_delay(self, fuse_number, selected_channel):
        fuse_number = str(fuse_number)
        user_input, was_success = self.get_user_input("Fuse delay", "Set delay of fuse " + fuse_number + " (MIN if "
                                                                                                         "empty)")
        if was_success:
            if user_input.isspace() or not user_input:
                self.send_command(lambda: self.power_supply.set_fuse_delay("MIN", "OUT" + fuse_number), "ps")
            else:
                self.send_command(lambda: self.power_supply.set_fuse_delay(user_input, "OUT" + fuse_number), "ps")
            self.send_command(lambda: self.power_supply.set_output_channel(selected_channel), "ps")

    def add_HMC8012_tab(self):
        self.multimeter_tab = QWidget()
        self.multimeter_tab.setAttribute(Qt.WA_DeleteOnClose)
        device_tab_layout = QGridLayout()

        output_box = QGroupBox("Output")
        output_box_layout = QGridLayout()
        self.multimeter_output_area = QLineEdit()
        self.multimeter_output_area.setReadOnly(True)
        output_box_layout.addWidget(self.multimeter_output_area, 0, 0)
        output_box.setLayout(output_box_layout)
        device_tab_layout.addWidget(output_box, 0, 0, 1, 1)

        common_command_box = QGroupBox("Common commands")
        common_command_box_layout = QGridLayout()
        HMC8012_common_commands_list, HMC8012_common_commands = self.create_common_commands_list(self.multimeter)

        common_commands_button = QPushButton()
        common_commands_button.setText("Apply")
        common_commands_button.clicked.connect(
            lambda: self.send_common_command(HMC8012_common_commands, HMC8012_common_commands_list, "m"))

        common_command_box_layout.addWidget(HMC8012_common_commands, 0, 0)
        common_command_box_layout.addWidget(common_commands_button, 0, 1)
        common_command_box.setLayout(common_command_box_layout)
        device_tab_layout.addWidget(common_command_box, 1, 0, 1, 1)

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
        device_tab_layout.addWidget(temperature_box, 0, 1, 2, 1)

        function_box = QGroupBox("Measurement options")
        function_box_layout = QGridLayout()
        function_box_layout.addWidget(QLabel("Selected measurement function:"), 0, 0)
        measurement_function = ComboBoxWithLast()
        measurement_function.addItem("DC V", self.multimeter.measure_voltage_dc)
        measurement_function.addItem("AC V", self.multimeter.measure_voltage_ac)
        measurement_function.addItem("DC I", self.multimeter.measure_current_dc)
        measurement_function.addItem("AC I", self.multimeter.measure_current_ac)
        measurement_function.addItem("Continuity", self.multimeter.measure_continuity)
        measurement_function.addItem("CAP", self.multimeter.measure_capacitance)
        measurement_function.addItem("Frequency (AC I)", self.multimeter.measure_frequency_current)
        measurement_function.addItem("Frequency (AC V)", self.multimeter.measure_frequency_voltage)
        measurement_function.addItem("Resistance (2-wire)", self.multimeter.measure_resistance)
        measurement_function.addItem("Resistance (4-wire)", self.multimeter.measure_fresistance)
        measurement_function.addItem("Diode tests", self.multimeter.measure_diode)
        measurement_function.setCurrentIndex(-1)
        measurement_function.selectedItemChanged.connect(self.configure_multimeter_measurements)
        function_box_layout.addWidget(measurement_function, 0, 1, 1, 2)

        function_box_layout.addWidget(QLabel("Mathematic function:"), 1, 0)
        mathematic_function = ComboBoxWithLast()
        mathematic_function.addItems([
            "AVERage",
            "LIMit",
            "NULL",
            "DB",
            "DBM",
            "POWer",
        ])
        mathematic_function.setCurrentIndex(-1)
        mathematic_function.selectedItemChanged.connect(self.set_mathematic_function)
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
        activate_statistic_function.setText("Set")
        activate_statistic_function.clicked.connect(lambda: self.send_command(statistic_function.currentData(), "m"))
        function_box_layout.addWidget(activate_statistic_function, 2, 2)

        self.switch_tab_bar()

        self.multimeter_tab.setLayout(device_tab_layout)
        self.tab_bar.addTab(self.multimeter_tab, "HMC8012")

    def activate_calc_function(self):
        sender = self.sender()
        if sender.isActivated:
            self.send_command(lambda: self.multimeter.toggle_calculate_function("OFF"), "m")
            sender.setText("Activate")
            sender.isActivated = False
        else:
            self.send_command(self.multimeter.toggle_calculate_function, "m")
            sender.setText("Deactivate")
            sender.isActivated = True

    def configure_temperature(self, unit, probe, sensor):
        kwargs = {}
        if unit is not None:
            kwargs.update({"unit": unit})
        if probe != '':
            kwargs.update({"probe_type": probe})
        if sensor != '':
            kwargs.update({"sensor_type": sensor})
        self.send_command(lambda: self.multimeter.measure_temperature(**kwargs), "m")

    def set_mathematic_function(self, last, new):
        sender = self.sender()
        if not (new < 0):
            if sender.currentText() == 'NULL':
                user_input, was_success = self.get_user_input("Maximum null", "Enter maximum NULL value (MIN if empty)")
                if was_success:
                    if user_input.isspace() or not user_input:
                        self.send_command(self.multimeter.set_calculate_null_offset, "m")
                    else:
                        self.send_command(lambda: self.multimeter.set_calculate_null_offset(user_input), "m")
                else:
                    sender.blockSignals(True)
                    sender.setCurrentIndex(last)
                    sender.blockSignals(False)
            self.send_command(lambda: self.multimeter.set_calculate_function(sender.currentText()), "m")

    def configure_multimeter_measurements(self, last, new):
        sender = self.sender()
        if not (new < 0):
            if sender.currentText() == 'Diode tests':
                func = sender.itemData(new)
                self.send_command(func, "m")
            else:
                func = sender.itemData(new)
                user_input, was_success = self.get_user_input("Measurement range",
                                                              "Enter desired range (AUTO if empty)")
                if was_success:
                    if user_input.isspace() or not user_input:
                        self.send_command(func, "m")
                    else:
                        self.send_command(lambda: func(user_input), "m")
                else:
                    sender.blockSignals(True)
                    sender.setCurrentIndex(last)
                    sender.blockSignals(False)

    def get_user_input(self, title, prompt):
        text, ok = QInputDialog.getText(self, title, prompt)
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
        return cmds_list, cmds_box

    def get_device_options(self):
        devices = {
            "HMC8012": "8012",
            "HMC8043": "8043"
            # "LowNoise": "COM5"
        }
        user_input, was_success = self.get_user_input("pySerial device address input", "Enter address for LowNoise, "
                                                                                       "if connected")
        if was_success:
            try:
                ser = serial.Serial(
                    port=user_input,
                    baudrate=115200,
                    bytesize=EIGHTBITS,
                    parity=PARITY_NONE,
                    stopbits=STOPBITS_ONE
                )
                ser.close()
                devices["LowNoise"] = user_input
            except serial.SerialException:
                self.handle_error("Device address is invalid")
        rm = pyvisa.ResourceManager('@py')
        resources = rm.list_resources()
        for res in resources:
            # if res != "ASRL5::INSTR":
            try:
                inst = rm.open_resource(res)
                idn = inst.query("*IDN?").split(",")[1]
                devices[idn] = res
                inst.close()
            except pyvisa.VisaIOError:
                pass
        rm.close()
        return devices

# devices[((inst.query("*IDN?")).split(","))[1]] = res