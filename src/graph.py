import tkinter as tk
#Don't know why the font isn't imported with the above import
from tkinter import font
import logging
from src.standard_calc import parse_line,special_functions,nested_contains

def float_range(low,high,increment=1):
    """similar to the builtin range function, but this 
    has support for a decimal increment value
    """
    y = low
    while high >= y:
        yield y
        y += round(increment,2)

class App:
    def __init__(self, master):
        """ Initialise basic graph attributes and draw
        grid lines
        """
        self.width, self.height = 600,600
        self.min_x,self.max_x = -10,10
        self.min_y,self.max_y = -10,10

        self.sf = self.width/(abs(self.min_x)+abs(self.max_x))
        self.float_plot_interval = 0.25
        
        #Create equation box and set fonts
        logging.info("Starting graphing mode")
        self.f = tk.Frame(master)
        self.equation_box = tk.Entry(self.f,font=font.Font(size=16))
        self.equation_box.grid(column=0,row=0)
        
        #Create button to draw the graph
        tk.Button(self.f,text="Graph it",
                command=lambda: self.graph_it()).grid(column=0,row=1)
        
        #Initialise graph canvas
        self.canvas = tk.Canvas(self.f,width=self.width,height=self.height,
                bg="#FFFFFF")
        self.canvas.grid(column=1,row=0)
        #Draw graph axes
        self.canvas.create_line(0,self.height/2,self.width,self.height/2,fill="#AAAAAA",tags="x-axis",
                width=2)
        self.canvas.create_line(self.width/2,0,self.width/2,self.height,fill="#AAAAAA",tags="y-axis",
                width=2)

        #Show gridlines every 1 unit
        grid_lines_every = 1
        for x in range(self.min_x,self.max_x+1,grid_lines_every):
            if x != 0:
                self.canvas.create_line([(x+self.width/2,0),
                    (x+self.width/2,self.height)],tags="grid_line",fill="#DADADA")

        for y in range(self.min_y,self.max_y+1,grid_lines_every):
            if y != 0:
                self.canvas.create_line([(0,y+self.height/2),
                    (self.width,y+self.height/2)],tags="grid_line",fill="#DADADA")
        
        #Show intervals every 5 units, add 1 to max_x, so it's
        #included in the loop
        for x in range(self.min_x,self.max_x+1,5):
            if x != self.max_x:
                self.canvas.create_text(x+self.width/2,self.height/2,anchor=tk.NW,
                    text=str(x),tags=("x-axis","label"))
            else:
                self.canvas.create_text(x+self.width/2,self.height/2,anchor=tk.NE,
                    text=str(x),tags=("x-axis","label"))
         
        for y in range(self.min_y,self.max_y+1,5):
            if y != self.max_y:
                self.canvas.create_text(self.width/2,y+self.height/2,anchor=tk.NW,
                    text=str(-1*y),tags=("y-axis","label"))
            else:
                self.canvas.create_text(self.width/2,y+self.height/2,anchor=tk.SW,
                    text=str(-1*y),tags=("y-axis","label"))

        self.canvas.scale("label",self.width/2,self.height/2,
            self.sf,self.sf)
        self.canvas.scale("grid_line",self.width/2,self.height/2,
            self.sf,self.sf)
        self.f.pack()

    def set_plot_interval(self,interval):
        """Sets the plot interval used for non-linear functions
        """
        self.float_plot_interval = interval
        logging.info("Plot interval {}".format(interval))
    
    def graph_it(self):
        """Create a graph from the contents of the equation box 
        replacing x with the current x value
        """
        self.canvas.delete("line")
        equation = self.equation_box.get()
        cords = []
        #If equation is linear, ie no powers then plot with interval
        #of 1, if not then plot at interval of 0.5
        logging.info("equation: {}".format(equation))
        
        if "^" in equation or nested_contains(special_functions,equation):
            plot_interval = self.float_plot_interval
        else:
            plot_interval = 1
        logging.info("Plot interval: {}".format(plot_interval))

        for x in float_range(self.min_x,self.max_x,plot_interval):
            try:
                cords.append((
                    round(x+self.width/2,2),#add half of width to center the origin
                    round(-1*(parse_line(equation,x=x)-self.height/2),2)
                ))
                #Invert the origin for y so -ve values are in bottom half and center
                #the origin by taking away half the height
            except Exception as e:
                #Catch errors and don't plot the values but don't crash
                logging.error("Error: {} \nRaised at x val: {}".format(e,x))

        logging.info("Coordinates: {}".format(cords)) 
        self.canvas.create_line(cords,tags="line")
        #Scale the line so it takes up all of the graph 
        self.canvas.scale("line",self.width/2,self.height/2,self.sf,self.sf)

