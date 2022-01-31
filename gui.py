# Demo rozbalovacieho menu dostupnynch zariadeni
# Connect pri Power supply vytvori instanciu PowerSupplyHMC804x s adresou prisluchajucou vybranemu zariadeniu
# Connect pri Multimeter vytvori instanciu DigitalMultimeterHMC8012 s adresou prisluchajucou vybranemu zariadeniu

import pyvisa
import tkinter as tk
from tkinter import ttk
from powersupply_HMC804x import PowerSupplyHMC804x
from multimeter_HMC8012 import DigitalMultimeterHMC8012


class InstrumentLoader(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        options = {'padx': 5, 'pady': 5}
        self.device_options = self.get_options()

        self.power_supply_label = ttk.Label(self, text="Power Supply:")
        self.power_supply_label.grid(column=0, row=0, sticky=tk.W, **options)
        self.multimeter_label = ttk.Label(self, text="Multimeter:")
        self.multimeter_label.grid(column=0, row=1, sticky=tk.W, **options)

        self.power_supply_selection = tk.StringVar()
        self.multimeter_selection = tk.StringVar()

        self.power_supply_menu = ttk.OptionMenu(
            self,
            self.power_supply_selection,
            "-",
            *self.device_options)
        self.power_supply_menu.grid(column=1, row=0, **options)
        self.multimeter_menu = ttk.OptionMenu(
            self,
            self.multimeter_selection,
            "-",
            *self.device_options)
        self.multimeter_menu.grid(column=1, row=1, **options)

        self.connect_power_supply_button = ttk.Button(self, text='Connect', command=self.create_power_supply)
        self.connect_power_supply_button.grid(column=2, row=0, sticky=tk.W, **options)
        self.connect_multimeter_button = ttk.Button(self, text='Connect', command=self.create_multimeter)
        self.connect_multimeter_button.grid(column=2, row=1, sticky=tk.W, **options)

        self.grid(padx=10, pady=10, sticky=tk.NSEW)

    def get_power_supply_address(self):
        return self.device_options.get(self.power_supply_selection.get())

    def create_power_supply(self):
        print("vytvaram instanciu PowerSupplyHMC804x")
        address = self.get_power_supply_address()
        if address is not None:
            return PowerSupplyHMC804x(address)
        print("zla addr")

    def get_multimeter_address(self):
        return self.device_options.get(self.multimeter_selection.get())

    def create_multimeter(self):
        print("vytvaram instanciu DigitalMultimeterHMC8012")
        address = self.get_multimeter_address()
        if address is not None:
            return DigitalMultimeterHMC8012(address)
        print("zla addr")

    def get_options(self):
        # Vytvor dictionary device_name:address
        devices = {}
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        for res in resources:
            inst = rm.open_resource(res)
            devices[((inst.query("*IDN?")).split(","))[1]] = res
            inst.close()
        rm.close()
        return devices


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('inst loader')
        self.geometry('300x100')
        self.resizable(False, False)

