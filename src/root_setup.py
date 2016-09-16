import tkinter as tk
from src import standard_calc, graph

root, f = None,None
def setup():
    global root, f
    """Create root level window, returning a frame
    """
    root = tk.Tk()
    f = root.Frame()
    
    #Make top level menubar
    self.menu_bar = tk.Menu(master)
    self.mode_bar = tk.Menu(self.menu_bar,tearoff=0)
    self.mode_bar.add_command(label="Standard",command=
            lambda master: standard_calc.App(f))
    self.mode_bar.add_command(label="Graphing",command=
            lambda master: graph.App(f))
    self.menu_bar.add_cascade(label="Mode",menu=self.mode_bar)

    #Dispaly menu_bar
    master.config(menu=self.menu_bar)
    
    return f

def switch_mode(


