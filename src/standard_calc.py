#!/usr/bin/env python3
import tkinter as tk
from tkinter import font
import logging
import types
import re
import math
from functools import partial
logging.basicConfig(level=logging.DEBUG)

max_precision_out = 5
special_functions = [
    ('sin', lambda x: math.sin(math.radians(x))),
    ('cos', lambda x: math.cos(math.radians(x))),
    ('tan', lambda x: math.tan(math.radians(x)))
]

def nested_in(tuple_list,search_for,i=0):
    """
    Look in list of tuples for string at a specific index(default 0)
    returns the tuple if string is found and false if not
    """
    for t in tuple_list:
        if search_for in t:
            return t
    return False

def nested_contains(tuple_list,lookup,i=0):
    for t in tuple_list:
        if t[i] in lookup:
            return True

    return False

def parse_line(calc_line,prev_ans=None,**kwargs):
    """
    Parses the line from the calculator screen, and replaces ANS with
    the previous answer and outputs the answer to calc_answer_screen.
    prev_ans is also set, however in case of an error such as division
    by 0 the previous answer defaults to 0
    """
    global special_functions
    def parse_special_func(arg_list):
        """Handle the use of special_functions recursively
        """
        arg_str = ""
        logging.debug("arg_list: {}".format(arg_list))
        #Go through arg_list and recall parse_special_funcif there's nested
        #sin's
        for i,elem in enumerate(arg_list):
            if nested_in(special_functions,elem) and i != 0:
                recieved_ans = parse_special_func(arg_list[i:])
                arg_str = arg_list[i-1] + recieved_ans

        logging.debug("arg_str {}".format(arg_str))
        #Get function required from special_functions
        func = nested_in(special_functions,arg_list[0])[1]
        if arg_str != "":
            ans = str(func(eval(arg_str)))
        else:
            ans = str(func(eval("".join(arg_list[2:]))))
        logging.debug("ans for sin is {}".format(ans))
        return ans


    #Replace "ANS" with the prev_ans
    calc_line = calc_line.replace("ANS",str(prev_ans))
    #Replace kwargs name with the value
    for name, value in kwargs.items():
        calc_line = calc_line.replace(name,str(value))
    #Replcae "^" with **
    calc_line = calc_line.replace("^","**")

    #Split calc_line by sin, cos and tan
    split_calc_line = re.split(r'(sin|cos|tan|\)|\()',calc_line)
    #Strip list of blank elems
    split_calc_line = list(filter(None,split_calc_line))
    logging.debug("Split_calc_line after regex: {}".format(split_calc_line))

    parsed_calc_line = []
    parsed = False
    i = 0
    while not parsed:
        if nested_in(special_functions,split_calc_line[i]):
            #Loop throught next list elems unitl final closing
            #brakcet is found, as to handle nested brackets
            
            #Set it to -1 so the opening bracket of the function
            #will be ignored
            closingsToIgnore = -1
            for j,elem in enumerate(split_calc_line[i:]):
                if elem == "(":
                    closingsToIgnore += 1
                #Closing bracket can be ignored as it belongs to
                #another opening bracket
                elif elem == ")" and closingsToIgnore > 0:
                    closingsToIgnore -= 1
                    #TODO don't need closing bracket if it's last
                elif elem == ")" and closingsToIgnore == 0:
                    parsed_calc_line.append(parse_special_func(split_calc_line[i:i+j]))
                    #Add j to i, so that any other nested sin's don't get 
                    #passed to parse_special_func again
                    i += j
        else:
            parsed_calc_line.append(split_calc_line[i])
        
        if i +1 == len(split_calc_line):
            parsed = True
        else:
            i += 1


    logging.debug("Parsed line to eval: {}".format(parsed_calc_line))
    try:
        ans = eval("".join(parsed_calc_line))
    except ZeroDivisionError as e:
        logging.error("Tried to divide by zero")
        raise(e)

    return ans

class App:
    global max_precision_out
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
            
            logging.info("Button: {} at row {} col {}".format(button,row,column))
            #Create a new row if needed
            if column == columns - 1:
                logging.info("Creating new row at: {}".format(button))
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

    def handle_parse_line(self):
        """Call parse_line, but set class specific attributes
        """
        self.prev_ans = self.calc_answer_screen['text']
        self.calc_answer_screen['text'] = round(
                parse_line(self.calc_screen.get(),self.prev_ans),max_precision_out)
        self.clear_on_next_button = True
        

    def clear_line(self):
        self.calc_screen.delete(0,'end')

