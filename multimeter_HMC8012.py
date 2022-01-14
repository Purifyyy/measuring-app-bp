from driver import InstrumentDriver


class DigitalMultimeter(InstrumentDriver):

    def __init__(self, address):
        super(DigitalMultimeter, self).__init__(address)

    def calc_average(self):
        value = self.manager.query("CALCulate:AVERage:AVERage?")
        return value

    def calc_average_clear(self):
        self.manager.wait("CALCulate:AVERage:CLEar")

    def calc_average_count(self):
        value = self.manager.query("CALCulate:AVERage:COUNt?")
        return value

    def calc_average_max(self):
        value = self.manager.query("CALCulate:AVERage:MAXimum?")
        return value

    def calc_average_min(self):
        value = self.manager.query("CALCulate:AVERage:MINimum?")
        return value

    def calc_average_ptpeak(self):
        value = self.manager.query("CALCulate:AVERage:PTPeak?")
        return value

    def get_calc_function(self):
        value = self.manager.query("CALCulate:FUNCtion?")
        return value

    def set_calc_function(self, measurement_function):
        self.manager.write("CALCulate:FUNCtion " + measurement_function)  # Predpokladam ze write, Usage v manualy nieje

    def get_calc_null_offset(self, parameter):
        value = self.manager.query("CALCulate:NULL:OFFSet? " + parameter)
        return value

    def set_calc_null_offset(self, parameter):
        self.manager.write("CALCulate:FUNCtion " + parameter)

    def measure_capacitance(self, measurement_range):
        value = self.manager.query("MEASure:CAPacitance? " + measurement_range)
        return value

    def measure_continuity(self):
        value = self.manager.query("MEASure:CONTinuity?")
        return value

    def measure_current_ac(self, measurement_range):
        value = self.manager.query("MEASure:CURRent:AC? " + measurement_range)
        return value

    def measure_current_dc(self, measurement_range):
        value = self.manager.query("MEASure:CURRent:DC? " + measurement_range)
        return value

    def measure_diode(self):
        value = self.manager.query("MEASure:DIODe?")
        return value

    def measure_frequency_current(self, measurement_range):
        value = self.manager.query("MEASure:FREQuency:CURRent " + measurement_range)
        return value

    def measure_frequency_voltage(self, measurement_range):
        value = self.manager.query("MEASure:FREQuency[:VOLTAGE]? " + measurement_range)
        return value

    def measure_fresistance(self, measurement_range):
        value = self.manager.query("MEASure:FRESistance? " + measurement_range)
        return value

    def measure_resistance(self, measurement_range):
        value = self.manager.query("MEASure:RESistance? " + measurement_range)
        return value

    def measure_temperature(self, probe_type, sensor_type):
        value = self.manager.query("MEASure:TEMPerature? " + probe_type + ',' + sensor_type)
        return value.split(',')

    def measure_voltage_ac(self, measurement_range):
        value = self.manager.query("MEASure[:VOLTage]:AC? " + measurement_range)
        return value

    def measure_voltage_dc(self, measurement_range):
        value = self.manager.query("MEASure[:VOLTage][:DC]? " + measurement_range)
        return value

    def get_temperature_unit(self):
        value = self.manager.query("UNIT:TEMPerature?")
        return value

    def set_temperature_unit(self, temperature_unit):
        self.manager.write("UNIT:TEMPerature " + temperature_unit)  # Predpokladam ze write, v manualy nieje Usage
