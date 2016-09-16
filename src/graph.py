import tkinter as tk
import logging
from src import standard_calc

class App(standard_calc.App):
    def __init__(self, master):
        logging.info("Starting graphing mode")
        self.f = tk.Frame(master)
        self.equation_box = tk.Entry(self.f)
        self.equation_box.grid(column=0,row=0)
        
        tk.Button(self.f,command=lambda: self.graph_it()).grid(column=0,row=1)
        
        self.canvas = tk.Canvas(self.f,width=400,height=400)
        self.canvas.grid(column=1,row=0)
        
        self.f.pack()

    def graph_it(self):
        """Create a graph from the contents of the equation box 
        replacing x with the current x value, this is done from 
        -20<x<20 and -20<y<20
        """
        equation = self.equation_box.get()
        cords = []
        for x in range(-20,20):
            #Since co-ordinates are measured from top left, offset all
            #points by -200,-200
            cords.append((x+200,eval(equation.replace("x",str(x)))+200))
        print(cords) 
        self.canvas.create_line(cords)
        
        self.canvas.scale(1,200,200,-10,-10)
