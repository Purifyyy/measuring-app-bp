import pyvisa

class InstrumentDriver():

    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.manager = rm.open_resource(port)

    @property
    def idn(self):
        return self.manager.query("*IDN?")

    def tst(self):
        self.manager.query("*TST?")

    def rst(self):
        self.manager.write("*RST")

    def local(self):
        self.manager.write("SYSTem:LOCal")

    def remote(self):
        self.manager.write("SYSTem:REMote")


