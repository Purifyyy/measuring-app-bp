from driver import InstrumentDriver


class PowerSupplyHMC804x(InstrumentDriver):

    def __init__(self, address):
        super(PowerSupplyHMC804x, self).__init__(address)

    def set_fuse_state(self, parameter='1'):
        # FUSE[:STATe] {ON | OFF | 0 | 1}
        # Activates or deactivates the fuse for the previous selected channel
        self.manager.write("FUSE " + str(parameter))

    def get_fuse_state(self):
        # FUSE[:STATe]?
        # Returns the fuse state of the previous selected channel
        value = self.manager.query("FUSE?")
        return value

    def set_fuse_delay(self, parameter='MIN'):
        # FUSE:DELay {<Delay>| MIN | MAX}
        # Defines a fuse delay for the previous selected channel
        #  <Delay> 10ms to 10s (adjustable in 1ms steps)
        #  MIN: 1.000E-02 (FUSE:DELay 0.01)
        #  MAX: 1.000E+01 (FUSE:DELay 10)
        self.manager.write("FUSE:DEL " + str(parameter))

    def get_fuse_delay(self):
        # FUSE:DELay? [MIN | MAX]
        # Returns the fuse delay time for the previous selected channel
        value = self.manager.query("FUSE:DEL?")
        return value

    def set_fuse_link(self, parameter='1'):
        # FUSE:LINK {1 | 2 | 3}
        # Combines the channel fuses (fuse linking) for the previous selected channel
        self.manager.write("FUSE:LINK " + str(parameter))

    def get_fuse_link(self, parameter='1'):
        # FUSE:LINK? {1 | 2 | 3}
        # Returns the combined fuses. If the fuse of channel 1 is linked with fuse of channel 2, a „1“ is
        # returned; when the fuse of channel 1 is not linked to the fuse of channel 2, it returns a „0“
        #  1: Fuse is linked
        #  0: Fuse is not linked
        value = self.manager.query("FUSE:LINK? " + str(parameter))
        return value

    def fuse_unlink(self, parameter='1'):
        # FUSE:UNLink {1 | 2 | 3}
        # Unlinks the channel fuses
        #  1 = channel CH1
        #  2 = channel CH2
        #  3 = channel CH3
        self.manager.write("FUSE:UNL " + str(parameter))

    def fuse_trip(self):
        # FUSE:TRIPed?
        # Returns the fuse trip of the previous selected channel
        #  1: Fuse is tripped.
        #  0: Fuse is not tripped
        value = self.manager.query("FUSE:TRIP?")
        return value

    def measure_scalar_current_dc(self):
        # MEASure[:SCALar]:CURRent[:DC]?
        # Returns the measured current value of the previous selected channel
        value = self.manager.query("MEAS:CURR?")
        return value

    def measure_scalar_voltage_dc(self):
        # MEASure[:SCALar][:VOLTage][:DC]?
        # Returns the measured voltage value of the previous selected channel
        value = self.manager.query("MEAS?")
        return value

    def measure_scalar_power(self):
        # MEASure[:SCALar]:POWer?
        # Returns the measured power value of the previous selected channel
        value = self.manager.query("MEAS:POW?")
        return value

    def measure_scalar_energy(self):
        # MEASure[:SCALar]:ENERgy?
        # Returns the measured current released energy value of the previous selected channel in Ws
        value = self.manager.query("MEAS:ENER?")
        return value

    def set_measure_scalar_energy_state(self, parameter='1'):
        # MEASure[:SCALar]:ENERgy:STATe {ON | OFF | 1 | 0}
        # Activates or deactivates the energy meter function
        self.manager.write("MEAS:ENER:STAT " + str(parameter))

    def get_measure_scalar_energy_state(self):
        # MEASure[:SCALar]:ENERgy:STATe?
        # Returns the energy meter state of the previous selected channel
        value = self.manager.query("MEAS:ENER:STAT?")
        return value

    def measure_scalar_energy_reset(self):
        # MEASure[:SCALar]:ENERgy:RESet
        # Resets the energy meter value of the previous selected channel
        self.manager.write("MEAS:ENER:RES")

    def set_output_state(self, parameter='0'):
        # OUTPut[:STATe] {OFF | ON | 0 | 1}
        # Activates or deactivates the previous selected channel and turning on the master output
        #  1: Channel and master output will be activated
        #  0: Channel will be deactivated
        self.manager.write("OUTP " + str(parameter))

    def get_output_state(self):
        # OUTPut[:STATe]?
        # Returns the output state
        value = self.manager.query("OUTP?")
        return value

    def set_output_channel_state(self, parameter='0'):
        # OUTPut:CHANnel[:STATe] {OFF | ON | 0 | 1}
        # Activates or deactivates the previous selected channel
        self.manager.write("OUTP:CHAN " + str(parameter))

    def get_output_channel_state(self):
        # OUTPut:CHANnel[:STATe]?
        # Returns the channel output state
        value = self.manager.query("OUTP:CHAN?")
        return value

    def set_output_master_state(self, parameter='0'):
        # OUTPut:MASTer[:STATe] {OFF | ON | 0 | 1}
        # Turning on / off all previous selected channels simultaneously
        #  1: Master output will be activated
        #  0: Master output will be deactivated
        self.manager.write("OUTP:MAST " + str(parameter))

    def get_output_master_state(self):
        # OUTPut:MASTer[:STATe]?
        # Returns the master output state
        value = self.manager.query("OUTP:MAST?")
        return value

    def set_source_current_level_immediate_amplitude(self, parameter='MIN'):
        # [SOURce:]CURRent[:LEVel][:IMMediate][:AMPLitude] {<Current>| MIN | MAX}
        # Sets the current value of the selected channel
        #  <Current> Adjustable in 0.1mA (I<1A) / 1mA (I≥1A) steps.
        #  MIN: 0.5mA
        #  MAX: 3.000A  (R&S®HMC8043)
        #       5.000A  (R&S®HMC8042)
        #       10.000A (R&S®HMC8041)
        self.manager.write("CURR " + str(parameter))

    def get_source_current_level_immediate_amplitude(self):
        # [SOURce:]CURRent[:LEVel][:IMMediate][:AMPLitude]? [MIN | MAX]
        # Returns the current value of the selected channel
        value = self.manager.query("CURR?")
        return value

    def vary_source_current_level_immediate_amplitude(self, parameter='UP'):
        # [SOURce:]CURRent[:LEVel][:IMMediate][:AMPLitude] {UP | DOWN}
        # Increases (UP) resp. decreases (DOWN) the current value of the selected channel
        self.manager.write("CURR " + str(parameter))

    def set_source_current_level_step_increment(self, parameter='DEF'):
        # [SOURce:]CURRent[:LEVel]:STEP[:INCRement) {<Numeric Value>| DEFault}
        # Defines the current step size for the CURR UP (CURR DOWN) command
        #  <Numeric Value> Adjustable in 0.1mA (I<1A) / 1mA (I≥1A) steps.
        #  5.0000E-04 to 3.000E+00  (R&S®HMC8043)
        #  5.0000E-04 to 5.000E+00  (R&S®HMC8042)
        #  5.0000E-04 to 1.0000E+01 (R&S®HMC8041)
        #  DEF: 1.0000E-01
        self.manager.write("CURR:STEP " + str(parameter))

    def get_source_current_level_step_increment(self):
        # [SOURce:]CURRent[:LEVel]:STEP[:INCRement]? [Default]
        # Returns the current step size
        value = self.manager.query("CURR:STEP?")
        return value

    def set_source_voltage_protection_state(self, parameter='0'):
        # [SOURce:]VOLTage:PROTection[:STATe] {OFF | ON | 0 | 1}
        # Activates (1) or deactivates (0) the OVP for the previous selected channel
        self.manager.write("VOLT:PROT " + str(parameter))

    def get_source_voltage_protection_state(self):
        # [SOURce:]VOLTage:PROTection[:STATe]?
        # Returns the OVP state of the previous selected channel
        value = self.manager.query("VOLT:PROT?")
        return value

    def set_source_voltage_protection_level(self, parameter='DEF'):
        # [SOURce:]VOLTage:PROTection:LEVel {<Voltage>| MIN | MAX | DEF}
        # Sets the OVP value of the previous selected channel
        #  <Voltage> 0V to 32.50V (adjustable in 1mV steps)
        #  MIN: 0.000E+00
        #  MAX: 3.2050E+01
        #  DEF: 3.2050E+01
        self.manager.write("VOLT:PROT:LEV " + str(parameter))

    def get_source_voltage_protection_level(self):
        # [SOURce:]VOLTage:PROTection:LEVel? [MIN | MAX | DEF]
        # Returns the OVP value of the previous selected channel
        value = self.manager.query("VOLT:PROT:LEV?")
        return value

    def source_voltage_protection_trip(self):
        # [SOURce:]VOLTage:PROTection:TRIPped?
        # Returns the OVP state of the previous selected channel
        #  1: OVP is tripped
        #  0: OVP is not tripped
        value = self.manager.query("VOLT:PROT:TRIP?")
        return value

    def source_voltage_protection_clear(self):
        # [SOURce:]VOLTage:PROTection:CLEar
        # Resets the OVP state of the selected channel
        self.manager.write("VOLT:PROT:CLE")

    def set_source_voltage_protection_mode(self, parameter='MEAS'):
        # [SOURce:]VOLTage:PROTection:MODE {MEASured | PROTected}
        # Sets the OVP mode for the previous selected channel
        #  MEASured: The OVP switches off if the measured value exceeds the threshold
        #  PROTected: If the adjusted threshold is exceeded the output of the instrument will be not switched on
        self.manager.write("VOLT:PROT:MODE " + str(parameter))

    def get_source_voltage_protection_mode(self):
        # [SOURce:]VOLTage:PROTection:MODE?
        # Returns the OVP mode for the previous selected channel
        value = self.manager.query("VOLT:PROT:MODE?")
        return value

    def set_source_power_protection_state(self, parameter='0'):
        # [SOURce:]POWer:PROTection[:STATe] {OFF | ON | 0 | 1}
        # Activates (1) or deactivates (0) the OPP for the previous selected channel
        self.manager.write("POW:PROT " + str(parameter))

    def get_source_power_protection_state(self):
        # [SOURce:]POWer:PROTection[:STATe]?
        # Returns the OPP state of the previous selected channel
        value = self.manager.query("POW:PROT?")
        return value

    def set_source_power_protection_level(self, parameter='DEF'):
        # [SOURce:]POWer:PROTection:LEVel {<Power>| MIN | MAX | DEF}
        # Sets the OPP value of the previous selected channel
        #  <Voltage> 0W to 33W (adjustable in 10mW steps)
        #  MIN: 0.000E+00
        #  MAX: 3.300E+01
        #  DEF: 3.300E+01
        self.manager.write("POW:PROT:LEV " + str(parameter))

    def get_source_power_protection_level(self):
        # [SOURce:]POWer:PROTection:LEVel? [MIN | MAX | DEF]
        # Returns the OPP value of the previous selected channel
        value = self.manager.query("POW:PROT:LEV?")
        return value

    def source_power_protection_trip(self):
        # [SOURce:]POWer:PROTection:TRIPped?
        # Returns the OPP state of the previous selected channel
        #  1: OPP is tripped
        #  0: OPP is not tripped
        value = self.manager.query("POW:PROT:TRIP?")
        return value

    def source_power_protection_clear(self):
        # [SOURce:]POWer:PROTection:CLEar
        # Resets the OPP state of the selected channel
        self.manager.write("POW:PROT:CLE")

    def set_source_voltage_ainput_state(self, parameter='0'):
        # [SOURce:]VOLTage:AINPut[:STATe] {OFF | ON | 0 | 1}
        # Activates (1) or deactivates (0) the Analog In function for the previous selected channel
        self.manager.write("VOLT:AINP " + str(parameter))

    def get_source_voltage_ainput_state(self):
        # [SOURce:]VOLTage:AINPut[:STATe]?
        # Returns the Analog In function state of the previous selected channel
        value = self.manager.query("VOLT:AINP?")
        return value

    def set_source_voltage_ainput_input(self, parameter='VOLT'):
        # [SOURce:]VOLTage:AINPut:INPut {VOLTage | CURRent}
        # Selects the input unit of the Analog In connector (terminal block) on the rear panel
        self.manager.write("VOLT:AINP:INP " + str(parameter))

    def get_source_voltage_ainput_input(self):
        # [SOURce:]VOLTage:AINPut:INPut?
        # Returns the input unit of the Analog In connector (terminal block) on the rear panel
        value = self.manager.query("VOLT:AINP:INP?")
        return value

    def set_source_voltage_ainput_mode(self, parameter='LIN'):
        # [SOURce:]VOLTage:AINPut:MODE {LINear | STEP}
        # Selects the mode of the Analog In connector (terminal block) on the rear panel
        #  LINear: Output voltage linear to the input voltage
        #  STEP: Reference value or zero depending on threshold
        self.manager.write("VOLT:AINP:MODE " + str(parameter))

    def get_source_voltage_ainput_mode(self):
        # [SOURce:]VOLTage:AINPut:MODE?
        # Returns the mode of the Analog In connector (terminal block) on the rear panel
        value = self.manager.query("VOLT:AINP:MODE?")
        return value

    def set_source_voltage_ainput_threshold(self, parameter='DEF'):
        # [SOURce:]VOLTage:AINPut:THReshold {<Threshold>| MIN | MAX | DEF}
        # Sets the threshold for the Analog In mode STEP
        #  <Threshold> 0V to 10V (adjustable in 100mV steps)
        #  MIN: 0.0E+00
        #  MAX: 1.00E+01
        #  DEF: 1.0E+00
        self.manager.write("VOLT:AINP:THR " + str(parameter))

    def get_source_voltage_ainput_threshold(self):
        # [SOURce:]VOLTage:AINPut:THReshold?
        # Returns the threshold of the Analog In mode STEP
        value = self.manager.query("VOLT:AINP:THR?")
        return value

    def set_source_voltage_ramp_state(self, parameter='0'):
        # [SOURce:]VOLTage:RAMP[:STATe] {OFF | ON | 0 | 1}
        # Activates (1) or deactivates (0) the EasyRamp function for the previous selected channel
        self.manager.write("VOLT:RAMP " + str(parameter))

    def get_source_voltage_ramp_state(self):
        # [SOURce:]VOLTage:RAMP[:STATe]?
        # Returns the EasyRamp function state of the previous selected channel
        value = self.manager.query("VOLT:RAMP?")
        return value

    def set_source_voltage_ramp_duration(self, parameter='DEF'):
        # [SOURce:]VOLTage:RAMP:DURation {<Duration>| MIN | MAX | DEF}
        # Sets the duration of the voltage ramp
        #  <Duration> 10ms to 10s
        #  MIN: 1.00E-02 (VOLT:RAMP:DUR 0.01)
        #  MAX: 1.000E+01 (VOLT:RAMP:DUR 10)
        #  DEF: 1.00E-02 (VOLT:RAMP:DUR 0.01)
        self.manager.write("VOLT:RAMP:DUR " + str(parameter))

    def get_source_voltage_ramp_duration(self):
        # [SOURce:]VOLTage:RAMP:DURation?
        # Returns the duration of the voltage ramp
        value = self.manager.query("VOLT:RAMP:DUR?")
        return value

    def set_source_voltage_level_immediate_amplitude(self, parameter='MIN'):
        # [SOURce:]VOLTage[:LEVel][:IMMediate][:AMPLitude] {<Voltage>| MIN | MAX}}
        # Sets the voltage value of the selected channel
        #  <Voltage> 0.000V to 32.050V (adjustable in 1mV steps)
        #  MIN 0.000E+00
        #  MAX 3.2050E+01
        self.manager.write("VOLT " + str(parameter))

    def get_source_voltage_level_immediate_amplitude(self):
        # [SOURce:]VOLTage[:LEVel][:IMMediate][:AMPLitude]? [MIN | MAX]
        # Returns the voltage value of the selected channel
        value = self.manager.query("VOLT?")
        return value

    def vary_source_voltage_level_immediate_amplitude(self, parameter='UP'):
        # [SOURce:]VOLTage[:LEVel][:IMMediate][:AMPLitude] {UP | DOWN}
        # Increases (UP) resp. decreases (DOWN) the voltage value of the selected channel
        self.manager.write("VOLT " + str(parameter))

    def set_source_voltage_level_step_increment(self, parameter='DEF'):
        # [SOURce:]VOLTage[:LEVel]:STEP[:INCRement) {<Numeric Value>| DEFault}
        # Defines the voltage step size for the VOLT UP (VOLT DOWN) command
        #  <Numeric Value> 0.000E+00 to 3.2050E+01 (adjustable in 1mV steps)
        #  DEF: 1.000E+00
        self.manager.write("VOLT:STEP " + str(parameter))

    def get_source_voltage_level_step_increment(self):
        # [SOURce:]VOLTage[:LEVel]:STEP[:INCRement)? [Default)
        # Returns the voltage step size
        value = self.manager.query("VOLT:STEP?")
        return value













