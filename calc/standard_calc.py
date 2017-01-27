#!/usr/bin/env python3
import tkinter as tk
from tkinter import font
import logging
import types
import re
import math
from functools import partial
from calc import calculations

max_precision_out = 5
logger = logging.getLogger(__name__)
class App:
    global max_precision_out
    def __init__(self, master, columns=5):
        #Define buttons and their functions/strings to be implemented
        #on press
        buttons = [
            ('1/x',('1/ANS', lambda: self.handle_parse_line())),
            ('+/-',('-1*ANS', lambda: self.handle_parse_line())),
            ('√','sqrt('),
            ('π','π'),
            ('e','e'),#
            ('sin','sin('),
            ('cos','cos('),
            ('tan','tan('),
            ('^','^'),
            ('C',self.clear_line),#
            ('7',7),
            ('8',8),
            ('9',9),
            ('(','('),
            (')',')'),#
            ('4',4),
            ('5',5),
            ('6',6),
            ('x','*'),
            ('/','/'),#
            ('1',1),
            ('2',2),
            ('3',3),
            ('+','+'),
            ('-','-'),#
            ('0',0),
            ('.','.'),
            ('x10','*10'),
            ('Ans','ANS'),
            ('=',lambda: self.handle_parse_line())
        ]
        #Define basic properties now to prevent ValueErrors on first button
        self.clear_on_next_button = False
        self.prev_ans = None
        
        # Make frame, child of master
        f = tk.Frame(master)
        #Initialize grid to 40px wide columns
        for column in range(columns):
            f.columnconfigure(column)

        #Create entry box to display the sum for the calculator, the sticky
        #option streches the textbox horizontally to use up all the space available
        self.calc_screen = tk.Entry(f,font=font.Font(size=16,family="Arial"))
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
            tk.Button(f,text=button,width=3,
                    relief=tk.GROOVE,overrelief=tk.GROOVE,
                    command=partial(self.button_handler,button_inf)).grid(
                            column=column,row=row)
            
            logger.info("Button: {} at row {} col {}".format(button,row,column))
            #Create a new row if needed
            if column == columns - 1:
                logger.info("Creating new row at: {}".format(button))
                row += 1
                column = 0
            else:
                column += 1
        f.pack() 
    def button_handler(self,buttonFunction):
        """
        Handles all button presses and either runs the
        function if the button is assigned to a function or class method
        or append the string or int to the calculator screen.
        """
        def handle_individual_func(buttonFunction):
            if isinstance(buttonFunction, types.MethodType) or \
                isinstance(buttonFunction, types.FunctionType):
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
        
        if isinstance(buttonFunction,tuple):
            for f in buttonFunction:
                handle_individual_func(f)
        else:
            handle_individual_func(buttonFunction)


    def handle_parse_line(self):
        """Call parse_line, but set class specific attributes
        """
        if self.prev_ans != None:
            self.prev_ans = self.calc_answer_screen['text']
        try:
            ans = round(calculations.parse_line(
                    self.calc_screen.get(),self.prev_ans),max_precision_out)
            self.prev_ans = ans
        except Exception as e:
            logger.error(e)
            ans = "Error"
            self.prev_ans = None

        self.calc_answer_screen['text'] = ans
        self.clear_on_next_button = True
        

    def clear_line(self):
        self.calc_screen.delete(0,'end')

