import pyvisa


class InstrumentDriver:

    def __init__(self, address):
        rm = pyvisa.ResourceManager()
        # HMC804x/HMC8012 Programmers Manual, 1.1.2 Ethernet (LAN) Interface
        self.manager = rm.open_resource('TCPIP::' + str(address) + '::5025::SOCKET')

    @property
    def idn(self):
        # *IDN?
        # Returns the instrument identification string
        return self.manager.query("*IDN?")

    def tst(self):
        # *TST?
        # Triggers selftests of the instrument and returns an error code in decimal form
        # „0“ indicates no errors occured
        return self.manager.query("*TST?")

    def rst(self):
        # *RST
        # Sets the instrument to a defined default status
        self.manager.write("*RST")

    def local(self):
        # SYSTem:LOCal
        # Sets the system to front panel control, the front panel control is unlocked
        self.manager.write("SYSTem:LOCal")

    def remote(self):
        # SYSTem:REMote
        # Sets the system to remote state, the front panel control is locked
        self.manager.write("SYSTem:REMote")


