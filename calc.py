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
        def parse_sin(arg_list):
            """Handle the use of sin recursively
            """
            arg_str = ""
            logging.info("arg_list: {}".format(arg_list))
            for i,elem in enumerate(arg_list):
                if elem == "sin" and i != 0:
                    recieved_ans = parse_sin(arg_list[i:])
                    print("Recieved ans: {}".format(recieved_ans))
                    arg_str = arg_list[i-1] + recieved_ans

            print("arg_str {}".format(arg_str))
            if arg_str != "":
                ans = str(math.sin(math.radians(eval(
                    arg_str))))
            else:
                ans = str(math.sin(math.radians(eval(
                    arg_list[2]))))
            logging.info("ans for sin is {}".format(ans))
            return ans


        calc_line = self.calc_screen.get()
        #Replace "ANS" with the prev_ans
        calc_line = calc_line.replace("ANS",str(self.prev_ans))

        #Split calc_line by sin, cos and tan
        split_calc_line = re.split(r'(sin|cos|tan|\)|\()',calc_line)
        #Strip list of blank elems
        split_calc_line = list(filter(None,split_calc_line))
        logging.info("Split_calc_line after regex: {}".format(split_calc_line))

        parsed_calc_line = []
        parsed = False
        i = 0
        while not parsed:
            print("i = {}".format(split_calc_line[i]))
            if split_calc_line[i] == "sin":
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
                    elif elem == ")" and closingsToIgnore == 0:
                        parse_sin(split_calc_line[i:i+j])
                        

            else:
                parsed_calc_line.append(split_calc_line[i])
            
            if i +1 == len(split_calc_line):
                parsed = True
            else:
                i += 1


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
