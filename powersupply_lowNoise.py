import serial


class PowerSupplyLowNoise:

    def __init__(self, address):
        try:
            # self.ser = serial.serial_for_url(url, ...) ---> url – Device name, number or URL
            self.ser = serial.Serial(
                port=address
                # , baudrate=38400,
                # timeout=0,
                # write_timeout=0.1
            )
        except serial.SerialException:
            print("connection attempt error")

    def close(self):
        self.ser.close()

    def set_channel_state(self, channel='1', state='e'):
        """Write"""
        # ch<n><e | d>
        # Enables or disables channel with corresponding number (n)
        #  e: Channel will be enabled
        #  d: Channel will be disabled
        inst = "ch" + str(channel) + str(state)
        self.ser.write(inst.encode())

    def set_voltage_level(self, channel='1', voltage='1000'):
        """Write"""
        # ch<n>s<voltage>
        # Sets the voltage value of channel with corresponding number (n)
        #  <voltage> 0.000V to XX.XXXV (adjustable in 1mV steps) <-------------------------------- MAX?
        inst = "ch" + str(channel) + "s" + str(voltage)
        self.ser.write(inst.encode())
