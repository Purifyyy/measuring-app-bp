import pyvisa


class InstrumentDriver:

    def __init__(self, address):
        rm = pyvisa.ResourceManager()
        # HMC804x/HMC8012 Programmers Manual, 1.1.2 Ethernet (LAN) Interface
        # USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]
        # ASRL[0]::host address::serial port::INSTR
        # TCPIP[board]::host address[::LAN device name][::INSTR]
        # TCPIP[board]::host address::port::SOCKET
        self.manager = rm.open_resource('TCPIP::' + str(address) + '::5025::SOCKET')

        # Odporucane pyvisa manualom, uvidim ci bude treba
        # self.read_termination = '\n'
        # self.write_termination = '\n'

        # HAMEG,‹device type›,‹serial number›,‹firmwareversion›
        # Example: HAMEG,HMC8012,12345,01.000
        self.identification = (self.idn()).replace(",", " ")

    @property
    def identification(self):
        return self._identification

    @identification.setter
    def identification(self, value):
        self._identification = value

    def idn(self):
        # *IDN?
        # Returns the instrument identification string
        return self.manager.query("*IDN?")

    def tst(self):
        # *TST?
        # Triggers self-tests of the instrument and returns an error code in decimal form
        # „0“ indicates no errors occured
        return self.manager.query("*TST?")

    def rst(self):
        # *RST
        # Sets the instrument to a defined default status
        self.manager.write("*RST")

    def local(self):
        # SYSTem:LOCal
        # Sets the system to front panel control, the front panel control is unlocked
        self.manager.write("SYST:LOC")

    def remote(self):
        # SYSTem:REMote
        # Sets the system to remote state, the front panel control is locked
        self.manager.write("SYST:REM")
