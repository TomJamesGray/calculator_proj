import tkinter as tk
from calculator import standard_calc

class Graphing(calc.App):
    def __init__(self, master):
        self.equation_box = tk.Entry(master)
        self.canvas = tk.Canvas(width=500,height=300)

