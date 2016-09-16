import tkinter as tk
import logging
from src import standard_calc

class App(standard_calc.App):
    def __init__(self, master):
        logging.info("Starting graphing mode")
        self.f = tk.Frame(master)
        self.equation_box = tk.Entry(self.f)
        self.canvas = tk.Canvas(self.f,width=500,height=300,bg="#FF00FF")


        self.f.pack()

