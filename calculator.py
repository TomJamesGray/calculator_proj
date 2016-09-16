#!/usr/bin/env python3
import tkinter as tk
from src import standard_calc, graph

if __name__ == "__main__":
    #Default to standard_calc on startup
    root = tk.Tk()
    app = standard_calc.App(root)
