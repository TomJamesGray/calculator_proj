import tkinter as tk
import logging
from src import standard_calc


class App(standard_calc.App):
    def __init__(self, master):
        global width,height

        self.width, self.height = 600,600
        self.min_x,self.max_x = -20,20

        logging.info("Starting graphing mode")
        self.f = tk.Frame(master)
        self.equation_box = tk.Entry(self.f)
        self.equation_box.grid(column=0,row=0)
        
        tk.Button(self.f,command=lambda: self.graph_it()).grid(column=0,row=1)
        
        self.canvas = tk.Canvas(self.f,width=self.width,height=self.height,bg="#FFFFFF")
        self.canvas.grid(column=1,row=0)
        #Draw graph axes
        self.canvas.create_line(0,self.height/2,self.width,self.height/2,fill="#AAAAAA",tags="x-axis",
                width=2)
        self.canvas.create_line(self.width/2,0,self.width/2,self.height,fill="#AAAAAA",tags="y-axis",
                width=2)

        #Show intervals every 5px
        
        self.f.pack()

    def graph_it(self):
        """Create a graph from the contents of the equation box 
        replacing x with the current x value, this is done from 
        -40<x<40 and -40<y<40
        """
        self.canvas.delete("line")
        equation = self.equation_box.get()
        cords = []
        for x in range(self.min_x,self.max_x):
            #Since co-ordinates are measured from top left, offset all
            #points by -200,-200
            cords.append((x+self.width/2,
                -1*(eval(equation.replace("x",str(x))))+self.height/2))
        print(cords) 
        self.canvas.create_line(cords,tags="line",smooth=True,splinesteps=20)
        
        sf = self.width/(abs(self.min_x)+abs(self.max_x))
        self.canvas.scale("line",self.width/2,self.height/2,sf,sf)
