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
from kivy.properties import ObjectProperty
import re
import math
from functools import partial
from calc import calculations

max_precision_out = 5
logger = logging.getLogger(__name__)

class Calculator(Widget):
    global max_precision_out
    screen = ObjectProperty(None)
    def __init__(self, columns=5,**kwargs):
        super(Calculator,self).__init__(**kwargs)
        #Define buttons and their functions/strings to be implemented
        #on press
        self.buttons = [
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
        for i,button in enumerate(self.buttons):
            grid.add_widget(Button(text=button[0],on_press=self.button_handler,id=str(i)))

        container.add_widget(grid)
        self.add_widget(container)

    def button_handler(self,button_instance):
        """
        Handles all button presses and either runs the
        function if the button is assigned to a function or class method
        or append the string or int to the calculator screen.
        """
        button_function = self.buttons[int(button_instance.id)][1]
        # print(buttonFunction())
        def handle_individual_func(button_function):
            if isinstance(button_function, types.MethodType) or \
                isinstance(button_function, types.FunctionType):
                button_function()
            else:
                #Only clear_on_next_button if the button isn't a function
                #this means the ANS can be incremented just by pressing '='
                if self.clear_on_next_button:
                    #Clear calc_screen
                    self.screen.text = ""
                    #Reset clear_on_next_button now
                    self.clear_on_next_button = False
                

                print("Button {} pressed".format(button_function))
                print(self.screen)
                self.screen.insert_text(str(button_function))
        
        if isinstance(button_function,tuple):
            for f in button_function:
                handle_individual_func(f)
        else:
            handle_individual_func(button_function)


    def handle_parse_line(self):
        """Call parse_line, but set class specific attributes
        """
        if self.prev_ans != None:
            self.prev_ans = self.screen.text
        try:
            ans = round(calculations.parse_line(
                    self.screen.text,self.prev_ans),max_precision_out)
            self.prev_ans = ans
        except Exception as e:
            logger.error(e)
            ans = "Error"
            self.prev_ans = None

        self.screen.text= str(ans)
        self.clear_on_next_button = True
        

    def clear_line(self):
        self.screen.text = ""

class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        Window.size=(400,400)
        calc = Calculator()
        return calc

def main():
    CalculatorApp().run()