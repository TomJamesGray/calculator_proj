#!/usr/bin/env python3
import tkinter as tk
import logging
import types
from functools import partial
logging.basicConfig(level=logging.DEBUG)

class App:
    def __init__(self, master, columns=5):
        buttons = [
            ('7',7),
            ('8',8),
            ('9',9),
            ('(','('),
            (')',')'),
            ('4',4),
            ('5',5),
            ('6',6),
            ('x','*'),
            ('/','/'),
            ('1',1),
            ('2',2),
            ('3',3),
            ('+','+'),
            ('-','-'),
            ('0',0),
            ('.','.'),
            ('x10','*10'),
            ('Ans','ANS'),
            ('=',self.parse_line)
        ]
        self.clear_on_next_button = False
        self.prev_ans = None
        # Make frame, child of master
        f = tk.Frame(master)
        #Initialize grid to 40px wide columns
        for column in range(columns):
            f.columnconfigure(column,minsize=40)
        f.pack()

        #Create entry box to display the sum for the calculator, the sticky
        #option streches the textbox horizontally to use up all the space available
        self.calc_screen = tk.Entry(f)
        self.calc_screen.grid(column=0,row=0,columnspan=columns,sticky=tk.E+tk.W)

        self.calc_answer_screen = tk.Label(f,justify='left')
        self.calc_answer_screen.grid(column=0,row=1,columnspan=columns,
                sticky=tk.E+tk.W)
        #Initialise variables for loop for button grid
        row, column = 2, 0
        
        # Loop through buttons and create button
        # with the command which will then be appended to the
        # "command line", with the exception of functions
        for button,button_inf in buttons:
            tk.Button(f,text=button,width=3,command=partial(
                self.button_handler,button_inf)).grid(column=column,row=row)
            
            logging.info("Button: {} at row {} col {}".format(button,row,column))
            #Create a new row if needed
            if column == columns - 1:
                logging.info("Creating new row at: {}".format(button))
                row += 1
                column = 0
            else:
                column += 1
    
    def button_handler(self,buttonFunction):
        if self.clear_on_next_button:
            #Clear calc_screen
            pass
        if isinstance(buttonFunction, types.MethodType):
            buttonFunction()
        else:
            #print(self.calc_screen.get())
            self.calc_screen.insert(tk.END,buttonFunction)
    
    def parse_line(self):
        calc_line = self.calc_screen.get()
        #Replace "ANS" with the prev_ans
        calc_line = calc_line.replace("ANS",str(self.prev_ans))
            
        try:
            #TODO Handling for dividing by zero, ANS, etc.
            ans = eval(calc_line)
            self.prev_ans = ans
        except ZeroDivisionError:
            ans = "can't divide by zero"
            #Default the previous answer to zero
            self.prev_ans = 0


        #Insert ans to answer_screen
        self.calc_answer_screen['text'] = ans

        self.clear_on_next_button = True
        return True
    
    def clear_line(self):
        return True



root = tk.Tk()
app = App(root)

root.mainloop()
