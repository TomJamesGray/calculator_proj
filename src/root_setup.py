import tkinter as tk
from src import standard_calc, graph

def setup(mode="standard"):
    """Create root level window, returning a frame
    """
    root = tk.Tk()
    #Make top level menubar
    menu_bar = tk.Menu(root)
    mode_bar = tk.Menu(menu_bar,tearoff=0)
    mode_bar.add_command(label="Standard",command=
            lambda: setup("standard"))
    mode_bar.add_command(label="Graphing",command=
        lambda: setup("graph"))
    menu_bar.add_cascade(label="Mode",menu=mode_bar)


    if mode == "standard":
        standard_calc.App(root)
    elif mode == "graph":
        app = graph.App(root)
        plot_interval_bar = tk.Menu(menu_bar,tearoff=0)
        plot_interval_bar.add_command(label="0.5",command=
            lambda: app.set_plot_interval(0.5))
        plot_interval_bar.add_command(label="0.25",command=
            lambda: app.set_plot_interval(0.25))
        plot_interval_bar.add_command(label="0.1",command=
            lambda: app.set_plot_interval(0.1))
        plot_interval_bar.add_command(label="0.05",command=
            lambda: app.set_plot_interval(0.05))
        menu_bar.add_cascade(label="Plot Interval", menu=plot_interval_bar)

    root.config(menu=menu_bar)
    root.mainloop()
