# Demo rozbalovacieho menu dostupnynch zariadeni, po stlaceni Connect tlacitka vrati string adresy (napr. ASRL2::INSTR)

import pyvisa
import tkinter as tk
from tkinter import ttk


class InstrumentLoader(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        options = {'padx': 5, 'pady': 5}
        self.device_options = self.get_options()

        self.power_supply_label = ttk.Label(self, text="Power Supply:")
        self.power_supply_label.grid(column=0, row=0, sticky=tk.W, **options)

        self.power_supply_selection = tk.StringVar()
        self.power_supply_selection.set("Select an Option")

        self.question_menu = ttk.OptionMenu(
            self,
            self.power_supply_selection,
            "-",
            *self.device_options)
        self.question_menu.grid(column=1, row=0, **options)

        self.connect_button = ttk.Button(self, text='Connect', command=self.get_power_supply_address)
        self.connect_button.grid(column=2, row=0, sticky=tk.W, **options)

        self.grid(padx=10, pady=10, sticky=tk.NSEW)

    def get_power_supply_address(self):
        return self.device_options.get(self.power_supply_selection.get())

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
        self.geometry('300x50')
        self.resizable(False, False)

