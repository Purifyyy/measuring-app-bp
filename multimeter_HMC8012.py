from driver import InstrumentDriver

class DigitalMultimeter(InstrumentDriver):
    VISA_PORT = 'ASRL5::INSTR'
    
    def __init__(self, port=VISA_PORT):
        super(DigitalMultimeter, self).__init__(port)
        
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

    def calc_function(self):
        value = self.manager.query("CALCulate:FUNCtion?")
        return value

