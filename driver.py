import pyvisa


def exception_handler(func):
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if func.__doc__ == "Query":
                if not result[0]:
                    return False, func.__doc__, result[2]
                return True, func.__doc__, result
            if result is None:
                return True, func.__doc__, func.__name__
            return result
        except pyvisa.VisaIOError:
            return False, func.__doc__, func.__doc__ + " failed" + " (" + func.__name__ + ")"
    return inner


class InstrumentDriver:

    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        # HMC804x/HMC8012 Programmers Manual, 1.1.2 Ethernet (LAN) Interface
        # USB[board]::manufacturer ID::model code::serial number[::USB interface number][::INSTR]
        # ASRL[0]::host address::serial port::INSTR
        # TCPIP[board]::host address[::LAN device name][::INSTR]
        # TCPIP[board]::host address::port::SOCKET
        # self.manager = rm.open_resource('TCPIP::' + str(address) + '::5025::SOCKET')
        #self.manager = self.rm.open_resource(address)

        # Odporucane pyvisa manualom, uvidim ci bude treba
        # self.read_termination = '\n'
        # self.write_termination = '\n'

        # HAMEG,‹device type›,‹serial number›,‹firmwareversion›
        # Example: HAMEG,HMC8012,12345,01.000
        #self.idn = ((self.manager.query("*IDN?")).split(","))[1]

    def __del__(self):
        #self.manager.close()
        self.rm.close()
        print("closing pyvisa resource")

    @property
    def idn(self):
        return self._idn

    @idn.setter
    def idn(self, value):
        self._idn = value

    @exception_handler
    def tst(self):
        """Query"""
        # *TST?
        # Triggers self-tests of the instrument and returns an error code in decimal form
        # „0“ indicates no errors occured
        return self.manager.query("*TST?")

    @exception_handler
    def rst(self):
        """Write"""
        # *RST
        # Sets the instrument to a defined default status
        self.manager.write("*RST")

    @exception_handler
    def local(self):
        """Write"""
        # SYSTem:LOCal
        # Sets the system to front panel control, the front panel control is unlocked
        self.manager.write("SYST:LOC")

    @exception_handler
    def remote(self):
        """Write"""
        # SYSTem:REMote
        # Sets the system to remote state, the front panel control is locked
        self.manager.write("SYST:REM")
