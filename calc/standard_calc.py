#!/usr/bin/env python3
import logging
import types
from kivy.config import Config
Config.set('graphics','resizable',0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import re
import math
from functools import partial
from calc import calculations

max_precision_out = 5
logger = logging.getLogger(__name__)

class Calculator(Widget):
    global max_precision_out
    def __init__(self, columns=5,**kwargs):
        super(Calculator,self).__init__(**kwargs)
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
        
        container = Widget()
        grid = GridLayout(size=(400,300),pos=(0,0),rows=6,cols=5)
        for button in buttons:
            grid.add_widget(Button(text=button[0]))

        container.add_widget(grid)
        self.add_widget(container)

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

class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        Window.size=(400,500)
        calc = Calculator()
        return calc

def main():
    CalculatorApp().run()