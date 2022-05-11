import random

from driver import InstrumentDriver, exception_handler


class DigitalMultimeterHMC8012(InstrumentDriver):

    def __init__(self, address):
        super(DigitalMultimeterHMC8012, self).__init__(address)

    @exception_handler
    def toggle_calculate_function(self, parameter='ON'):
        """Write"""
        # CALCulate[:STATe] {OFF | ON}
        # Turns with the CALC FUNC command selected calculation function ON or OFF
        self.manager.write("CALC " + str(parameter))

    @exception_handler
    def calculate_function_state(self):
        """Query"""
        # CALCulate[:STATe]?
        # Returns the state (ON/OFF) of the CALC FUNC command selected calculation function
        value = self.manager.query("CALC?")
        return value

    @exception_handler
    def calculate_average_average(self):
        """Query"""
        # CALCulate:AVERage:AVERage?
        # Returns the mean value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALC:AVER:AVER?")
        return value

    @exception_handler
    def calculate_average_clear(self):
        """Write"""
        # CALCulate:AVERage:CLEar
        # Resets all statistic function values
        self.manager.write("CALC:AVER:CLE")

    @exception_handler
    def calculate_average_count(self):
        """Query"""
        # CALCulate:AVERage:COUNt?
        # Returns the number of statistic measurement counts
        value = self.manager.query("CALC:AVER:COUN?")
        return value

    @exception_handler
    def calculate_average_maximum(self):
        """Query"""
        # CALCulate:AVERage:MAXimum?
        # Returns the maximum value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALC:AVER:MAX?")
        return value

    @exception_handler
    def calculate_average_minimum(self):
        """Query"""
        # CALCulate:AVERage:MINimum?
        # Returns the minimum value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALC:AVER:MIN?")
        return value

    @exception_handler
    def calculate_average_ptpeak(self):
        """Query"""
        # CALCulate:AVERage:PTPeak?
        # Returns the peak to peak value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALC:AVER:PTP?")
        return value

    @exception_handler
    def get_calculate_function(self):
        """Query"""
        # CALCulate:FUNCtion?
        # Returns the calculation function
        #  NULL: Null function
        #  DB: dB function (available in DC V AC V, DC I, AC I)
        #  DBM: dBm function (available in DC V AC V, DC I, AC I)
        #  AVER: Statistic measurements
        #  LIM: Limit lines
        #  POW: DC power value (available in DC V/DC I or DC I/DC V mode)
        value = self.manager.query("CALC:FUNC?")
        return value

    @exception_handler
    def set_calculate_function(self, measurement_function='NULL'):
        """Write"""
        # CALCulate:FUNCtion {NULL | DB | DBM | AVERage | LIMit | POWer}
        # Sets the calculation function, but does not activate the function
        #  NULL: Null function
        #  DB: dB function
        #  DBM: dBm function
        #  AVERage: Statistic measurements
        #  LIMit: Limit lines
        #  POWer: Power display
        self.manager.write("CALC:FUNC " + str(measurement_function))

    @exception_handler
    def get_calculate_null_offset(self, parameter='MIN'):
        """Query"""
        # CALCulate:NULL:OFFSet? {MINimum | MAXimum}
        # Returns the maximum null value depending on the activated measurement function
        value = self.manager.query("CALC:NULL:OFFS? " + str(parameter))
        return value

    @exception_handler
    def set_calculate_null_offset(self, parameter='MIN'):
        """Write"""
        # CALCulate:NULL:OFFSet {<Value> | MINimum | MAXimum}
        # Sets the maximum null value depending on the activated measurement function
        self.manager.write("CALC:NULL:OFF " + str(parameter))

    @exception_handler
    def measure_capacitance(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:CAPacitance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for capacitance measurements
        #  <Range> 5nF, 50nF, 500nF, 5µF, 50µF, 500µF
        #  AUTO: Auto range selection
        #  MIN: 5nF range selection
        #  MAX: 500µF range selection
        #  DEF: 5nF range selection
        value = self.manager.query("MEAS:CAP? " + str(measurement_range))
        return value

    @exception_handler
    def measure_continuity(self):
        """Query"""
        # MEASure:CONTinuity?
        # Configures the instrument for continuity measurements
        # Returns a single reading, the range is fixed (4000Ω)
        value = self.manager.query("MEAS:CONT?")
        return value

    @exception_handler
    def measure_current_ac(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:CURRent:AC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for AC I measurements
        #  <Range> 20mA, 200mA, 2A, 10A
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEF: 20mA range selection
        value = self.manager.query("MEAS:CURR:AC? " + str(measurement_range))
        return value

    @exception_handler
    def measure_current_dc(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:CURRent:DC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for DC I measurements
        #  <Range> 20mA, 200mA, 2A, 10A
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEF: 20mA range selection
        value = self.manager.query("MEAS:CURR:DC? " + str(measurement_range))
        return value

    @exception_handler
    def measure_diode(self):
        """Query"""
        # MEASure:DIODe?
        # Configures the instrument for diode tests
        # Returns a single reading, the range is fixed (5V)
        value = self.manager.query("MEAS:DIOD?")
        return value

    @exception_handler
    def measure_frequency_current(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:FREQuency:CURRent [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for frequency measurements with main function AC I
        #  <Range> AC current: 20mA, 200mA (5Hz to 10kHz)
        #                      2A, 10A (5Hz to 5kHz)
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEFault: 20mA range selection
        value = self.manager.query("MEAS:FREQ:CURR " + str(measurement_range))
        return value

    @exception_handler
    def measure_frequency_voltage(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:FREQuency[:VOLTAGE]? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for frequency measurements with main function AC V
        #  <Range> AC voltage: 400mV, 4V, 40V, 400V, 750V (5Hz to 700kHz)
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEFault: 400mV range selection
        value = self.manager.query("MEAS:FREQ? " + str(measurement_range))
        return value

    @exception_handler
    def measure_fresistance(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:FRESistance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for 4-wire resistance measurements
        #  <Range> 400Ω, 4kΩ, 40kΩ, 400kΩ, 4MΩ
        #  AUTO: Auto range selection
        #  MIN:	400Ω
        #  MAX:	4MΩ
        #  DEF:	400Ω
        value = self.manager.query("MEAS:FRES? " + str(measurement_range))
        return value

    @exception_handler
    def measure_resistance(self, measurement_range='AUTO'):
        """Query"""
        # MEASure:RESistance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for 2-wire resistance measurements
        #  <Range> 400Ω, 4kΩ, 40kΩ, 400kΩ, 4MΩ, 40MΩ, 250MΩ
        #  AUTO: Auto range selection
        #  MIN:	400Ω range selection
        #  MAX: 250MΩ range selection
        #  DEFault: 400Ω range selection
        value = self.manager.query("MEAS:RES? " + str(measurement_range))
        return value

    @exception_handler
    def measure_temperature(self, probe_type='DEF', sensor_type='DEF', unit='C'):
        """Query"""
        # MEASure:TEMPerature? [{<Probe_Type>| DEF}[,{<Type>| DEF}]
        # Configures the instrument for temperature measurements
        #  <Probe_Type> FRTD|RTD|DEF:RTD
        #  <Type> PT100|PT500|PT1000|DEF:PT100
        ret = self.set_temperature_unit(unit)
        if not ret[0]:
            return ret
        value = self.manager.query("MEAS:TEMP? " + str(probe_type) + ',' + str(sensor_type))
        return value

    @exception_handler
    def measure_voltage_ac(self, measurement_range='AUTO'):
        """Query"""
        # MEASure[:VOLTage]:AC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for AC V measurements
        #  <Range> 400mV, 4V, 40V, 400V, 750V
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEF: 400mV range selection
        value = self.manager.query("MEAS:AC? " + str(measurement_range))
        return value

    @exception_handler
    def measure_voltage_dc(self, measurement_range='AUTO'):
        """Query"""
        # MEASure[:VOLTage][:DC]? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for DC V measurements
        #  <Range> 400mV, 4V, 40V, 400V, 750V
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEF: 400mV range selection
        value = self.manager.query("MEAS? " + str(measurement_range))
        return value

    @exception_handler
    def get_temperature_unit(self):
        """Query"""
        # UNIT:TEMPerature?
        # Returns the unit of the temperature measurement function
        #  C: °C is activated
        #  K: Kelvins is activated
        #  F: °F is activated
        value = self.manager.query("UNIT:TEMP?")
        return value

    @exception_handler
    def set_temperature_unit(self, temperature_unit='C'):
        """Write"""
        # UNIT:TEMPerature {C | K | F}
        # Selects the unit of the temperature measurement function
        #  C: °C
        #  K: Kelvins
        #  F: °F
        self.manager.write("UNIT:TEMP " + str(temperature_unit))
