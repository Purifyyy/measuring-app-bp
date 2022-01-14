import pyvisa


class InstrumentDriver():

    def __init__(self, address):
        rm = pyvisa.ResourceManager()
        # Podla HMC804x/HMC8012 manualu, 1.1.2 Ethernet (LAN) Interface
        self.manager = rm.open_resource('TCPIP::' + address + '::5025::SOCKET')

    @property
    def idn(self):
        return self.manager.query("*IDN?")

    def tst(self):
        return self.manager.query("*TST?")

    def rst(self):
        self.manager.write("*RST")

    def local(self):
        self.manager.write("SYSTem:LOCal")

    def remote(self):
        self.manager.write("SYSTem:REMote")
