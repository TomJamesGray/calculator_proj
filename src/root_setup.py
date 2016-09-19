import tkinter as tk
from src import standard_calc, graph

def setup(mode="standard"):
    """Create root level window, returning a frame
    """
    root = tk.Tk()
    root.config(bg='#282828')
    #Make top level menubar
    menu_bar = tk.Menu(root)
    mode_bar = tk.Menu(menu_bar,tearoff=0)
    mode_bar.add_command(label="Standard",command=
            lambda: setup("standard"))
    mode_bar.add_command(label="Graphing",command=
        lambda: setup("graph"))
    menu_bar.add_cascade(label="Mode",menu=mode_bar)

    #Dispaly menu_bar
    root.config(menu=menu_bar)

    if mode == "standard":
        standard_calc.App(root)
    elif mode == "graph":
        graph.App(root)

    root.mainloop()

