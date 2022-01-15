from driver import InstrumentDriver


class DigitalMultimeterHMC8012(InstrumentDriver):

    def __init__(self, address):
        super(DigitalMultimeterHMC8012, self).__init__(address)

    def calc_average_mean(self):
        # CALCulate:AVERage:AVERage?
        # Returns the mean value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALCulate:AVERage:AVERage?")
        return value

    def calc_average_clear(self):
        # CALCulate:AVERage:CLEar
        # Resets all statistic function values
        self.manager.wait("CALCulate:AVERage:CLEar")

    def calc_average_count(self):
        # CALCulate:AVERage:COUNt?
        # Returns the number of statistic measurement counts
        value = self.manager.query("CALCulate:AVERage:COUNt?")
        return value

    def calc_average_max(self):
        # CALCulate:AVERage:MAXimum?
        # Returns the maximum value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALCulate:AVERage:MAXimum?")
        return value

    def calc_average_min(self):
        # CALCulate:AVERage:MINimum?
        # Returns the minimum value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALCulate:AVERage:MINimum?")
        return value

    def calc_average_ptpeak(self):
        # CALCulate:AVERage:PTPeak?
        # Returns the peak to peak value of the statistic function depending on the activated measurement function
        value = self.manager.query("CALCulate:AVERage:PTPeak?")
        return value

    def get_calc_function(self):
        # CALCulate:FUNCtion?
        # Returns the calculation function
        #  NULL: Null function
        #  DB: dB function (available in DC V AC V, DC I, AC I)
        #  DBM: dBm function (available in DC V AC V, DC I, AC I)
        #  AVER: Statistic measurements
        #  LIM: Limit lines
        #  POW: DC power value (available in DC V/DC I or DC I/DC V mode)
        value = self.manager.query("CALCulate:FUNCtion?")
        return value

    def set_calc_function(self, measurement_function='NULL'):
        # CALCulate:FUNCtion {NULL | DB | DBM | AVERage | LIMit | POWer}
        # Sets the calculation function, but does not activate the function
        #  NULL: Null function
        #  DB: dB function
        #  DBM: dBm function
        #  AVERage: Statistic measurements
        #  LIMit: Limit lines
        #  POWer: Power display
        self.manager.write("CALCulate:FUNCtion " + str(measurement_function))  # Predpokladam ze write, Usage v manualy nieje

    def get_calc_null_offset(self, parameter='MINimum'):
        # CALCulate:NULL:OFFSet? {MINimum | MAXimum}
        # Returns the maximum null value depending on the activated measurement function
        value = self.manager.query("CALCulate:NULL:OFFSet? " + str(parameter))
        return value

    def set_calc_null_offset(self, parameter='MINimum'):
        # CALCulate:NULL:OFFSet {<Value> | MINimum | MAXimum}
        # Sets the maximum null value depending on the activated measurement function
        self.manager.write("CALCulate:FUNCtion " + str(parameter))

    def measure_capacitance(self, measurement_range='AUTO'):
        # MEASure:CAPacitance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for capacitance measurements
        #  <Range> 5nF, 50nF, 500nF, 5µF, 50µF, 500µF
        #  AUTO: Auto range selection
        #  MIN: 5nF range selection
        #  MAX: 500µF range selection
        #  DEF: 5nF range selection
        value = self.manager.query("MEASure:CAPacitance? " + str(measurement_range))
        return value

    def measure_continuity(self):
        # MEASure:CONTinuity?
        # Configures the instrument for continuity measurements
        # Returns a single reading, the range is fixed (4000Ω)
        value = self.manager.query("MEASure:CONTinuity?")
        return value

    def measure_current_ac(self, measurement_range='AUTO'):
        # MEASure:CURRent:AC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for AC I measurements
        #  <Range> 20mA, 200mA, 2A, 10A
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEF: 20mA range selection
        value = self.manager.query("MEASure:CURRent:AC? " + str(measurement_range))
        return value

    def measure_current_dc(self, measurement_range='AUTO'):
        # MEASure:CURRent:DC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for DC I measurements
        #  <Range> 20mA, 200mA, 2A, 10A
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEF: 20mA range selection
        value = self.manager.query("MEASure:CURRent:DC? " + str(measurement_range))
        return value

    def measure_diode(self):
        # MEASure:DIODe?
        # Configures the instrument for diode tests
        # Returns a single reading, the range is fixed (5V)
        value = self.manager.query("MEASure:DIODe?")
        return value

    def measure_frequency_current(self, measurement_range='AUTO'):
        # MEASure:FREQuency:CURRent [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for frequency measurements with main function AC I
        #  <Range> AC current: 20mA, 200mA (5Hz to 10kHz)
        #                      2A, 10A (5Hz to 5kHz)
        #  AUTO: Auto range selection
        #  MIN: 20mA range selection
        #  MAX: 10A range selection
        #  DEFault: 20mA range selection
        value = self.manager.query("MEASure:FREQuency:CURRent " + str(measurement_range))
        return value

    def measure_frequency_voltage(self, measurement_range='AUTO'):
        # MEASure:FREQuency[:VOLTAGE]? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for frequency measurements with main function AC V
        #  <Range> AC voltage: 400mV, 4V, 40V, 400V, 750V (5Hz to 700kHz)
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEFault: 400mV range selection
        value = self.manager.query("MEASure:FREQuency[:VOLTAGE]? " + str(measurement_range))
        return value

    def measure_fresistance(self, measurement_range='AUTO'):
        # MEASure:FRESistance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for 4-wire resistance measurements
        #  <Range> 400Ω, 4kΩ, 40kΩ, 400kΩ, 4MΩ
        #  AUTO: Auto range selection
        #  MIN:	400Ω
        #  MAX:	4MΩ
        #  DEF:	400Ω
        value = self.manager.query("MEASure:FRESistance? " + str(measurement_range))
        return value

    def measure_resistance(self, measurement_range='AUTO'):
        # MEASure:RESistance? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for 2-wire resistance measurements
        #  <Range> 400Ω, 4kΩ, 40kΩ, 400kΩ, 4MΩ, 40MΩ, 250MΩ
        #  AUTO: Auto range selection
        #  MIN:	400Ω range selection
        #  MAX: 250MΩ range selection
        #  DEFault: 400Ω range selection
        value = self.manager.query("MEASure:RESistance? " + str(measurement_range))
        return value

    def measure_temperature(self, probe_type='DEF', sensor_type='DEF'):
        # MEASure:TEMPerature? [{<Probe_Type>| DEF}[,{<Type>| DEF}]
        # Configures the instrument for temperature measurements
        #  <Probe_Type> FRTD|RTD|DEF:RTD
        #  <Type> PT100|PT500|PT1000|DEF:PT100
        value = self.manager.query("MEASure:TEMPerature? " + str(probe_type) + ',' + str(sensor_type))
        return value

    def measure_voltage_ac(self, measurement_range='AUTO'):
        # MEASure[:VOLTage]:AC? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for AC V measurements
        #  <Range> 400mV, 4V, 40V, 400V, 750V
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEF: 400mV range selection
        value = self.manager.query("MEASure[:VOLTage]:AC? " + str(measurement_range))
        return value

    def measure_voltage_dc(self, measurement_range='AUTO'):
        # MEASure[:VOLTage][:DC]? [{<Range>| AUTO | MIN | MAX | DEF}]
        # Configures the instrument for DC V measurements
        #  <Range> 400mV, 4V, 40V, 400V, 750V
        #  AUTO: Auto range selection
        #  MIN: 400mV range selection
        #  MAX: 750V range selection
        #  DEF: 400mV range selection
        value = self.manager.query("MEASure[:VOLTage][:DC]? " + str(measurement_range))
        return value

    def get_temperature_unit(self):
        # UNIT:TEMPerature?
        # Returns the unit of the temperature measurement function
        #  C: °C is activated
        #  K: Kelvins is activated
        #  F: °F is activated
        value = self.manager.query("UNIT:TEMPerature?")
        return value

    def set_temperature_unit(self, temperature_unit='C'):
        # UNIT:TEMPerature {C | K | F}
        # Selects the unit of the temperature measurement function
        #  C: °C
        #  K: Kelvins
        #  F: °F
        self.manager.write("UNIT:TEMPerature " + str(temperature_unit))  # Predpokladam ze write, v manualy nieje Usage
