#!/usr/bin/env python3
import tkinter as tk
import logging
import types
import re
import math
from functools import partial
logging.basicConfig(level=logging.DEBUG)

class App:
    def __init__(self, master, columns=5):
        #Define buttons and their functions/strings to be implemented
        #on press
        buttons = [
            ('sin','sin('),
            ('cos','cos('),
            ('tan','tan('),
            ('^','**'),
            ('C',self.clear_line),
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
        #Define basic properties now to prevent ValueErrors on first button
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
        """
        Handles all button presses and either runs the
        function if the button is assigned to a function or class method
        or append the string or int to the calculator screen.
        """

        if isinstance(buttonFunction, types.MethodType):
            buttonFunction()
        else:
            #Only clear_on_next_button if the button isn't a function
            #this means the ANS can be incremented just by pressing '='
            if self.clear_on_next_button:
                #Clear calc_screen
                self.calc_screen.delete(0,'end')
                #Reset clear_on_next_button now
                self.clear_on_next_button = False
            
            self.calc_screen.insert(tk.END,buttonFunction)
    
    def parse_line(self):
        """
        Parses the line from the calculator screen, and replaces ANS with
        the previous answer and outputs the answer to calc_answer_screen.
        prev_ans is also set, however in case of an error such as division
        by 0 the previous answer defaults to 0
        """

        calc_line = self.calc_screen.get()
        #Replace "ANS" with the prev_ans
        calc_line = calc_line.replace("ANS",str(self.prev_ans))

        #Split calc_line by "(" and ")", so sin,cos and tan with nested
        #brackets can be worked out easier
        split_calc_line = re.split(r'[\(|\)]',calc_line)
        print(split_calc_line)
        parsed_calc_line = []
        parsed = False
        for i,elem in enumerate(split_calc_line):
            if elem.endswith("sin"):
                parsed_calc_line.append(eval
                #Evaluate the next item of the array as the arg for 
                #the sin function, using degrees, which have to be
                #converted to raidans firstly
                parsed_calc_line.append(str(math.sin(math.radians(
                    eval(split_calc_line[i+1])))))
                split_calc_line[i+1] = ""
            else:
                parsed_calc_line.append(elem)
        
        print(parsed_calc_line)
        ans = eval("".join(parsed_calc_line))
        try:
            #TODO Handling for dividing by zero, ANS, etc.
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
        self.calc_screen.delete(0,'end')

root = tk.Tk()
app = App(root)

root.mainloop()
