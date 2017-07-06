#!/usr/bin/env python3
import logging
import types
from kivy.config import Config
Config.set('graphics','resizable',0)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle,Color,Translate
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
        grid = GridLayout(size=(350,300),pos=(0,0),rows=6,cols=5)
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
        
    def graph_mode(self):
        """
        Switch to the graphing mode
        :return:
        """
        Window.size = (600,450)
        self.clear_widgets()
        self.add_widget(GraphingCalc(pos=(0,0),width=600,height=450))

    def clear_line(self):
        self.screen.text = ""

class GraphingCalc(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.x_max = 6
        self.x_min = -6
        self.x_step = 1
        self.y_max = 6
        self.y_min = -6
        self.y_step = 1
        self.graph_width = 400
        self.graph_height = 410
        self.graph = RelativeLayout(pos=(200,0),width=self.graph_width,height=self.graph_height)
        # Add graph axes
        with self.graph.canvas:
            Color(1,1,1,1)
            Rectangle(pos=(0,0),size=self.graph.size)
            Color(0,0,0,1)
            # Major Y axis
            self.generate_axes(self.carte_to_px(0, self.y_min), (1, 410), (0, 0, 0, 1))
            # Major X axis
            self.generate_axes(self.carte_to_px(self.x_min, 0), (400, 1), (0, 0, 0, 1))

            # Minor x axes
            for i in range(self.x_min, self.x_max + self.x_step, self.x_step):
                self.generate_axes(self.carte_to_px(self.x_min, i), (400, 1), (.1, .1, .1, .4))

            # Minor y axes
            for i in range(self.y_min, self.y_max + self.y_step, self.y_step):
                self.generate_axes(self.carte_to_px(i, self.y_min), (1, 410), (.1, .1, .1, .4))

            # Add x labels
            x_labels = list(range(self.x_min,self.x_max+self.x_step,self.x_step))
            x_spacing = self.graph_width/len(x_labels)

            for i,lbl in enumerate(x_labels):
                print("Adding label for x={}".format(x_labels[i]))
                self.add_widget(
                    Label(pos=self.carte_to_px(x_labels[i],0), font_size="8sp", width=7, height=10,
                          color=(0, 0, 0, 1), text=str(x_labels[i])))

            # Add y labels
            y_labels = list(range(self.y_min, self.y_max + self.y_step, self.y_step))
            y_spacing = self.graph_height / len(y_labels)

            for i, lbl in enumerate(y_labels):
                # Don't repeat 0 as already done on x label run
                if y_labels[i] == 0:
                    continue
                print("Adding label for y={}".format(y_labels[i]))
                self.add_widget(
                    Label(pos=self.carte_to_px(0,y_labels[i]), font_size="8sp", width=7, height=10,
                          color=(0, 0, 0, 1), text=str(x_labels[i])))

            Translate(xy=self.pos)

        self.add_widget(self.graph)

    def carte_to_px(self,carte_x,carte_y):
        """
        Converts a given cartesian co-ordinate for the graph to the pixels for drawing
        :param carte_x: X value for co-ordinate
        :param carte_y: Y Value for co-ordinate
        :return: (X,Y) tuple with co-ordinates in pixels on the graph
        """
        dx = carte_x - self.x_min
        dy = carte_y - self.y_min
        return (int(dx*self.graph_width/(self.x_max-self.x_min)),int(dy*self.graph_height)/(self.y_max-self.y_min))

    def generate_axes(self,pos,size,col):
        with self.graph.canvas:
            Color(*col)
            Rectangle(pos=pos,size=size)
            # Translate(xy=self.pos)

class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        Window.size=(350,450)
        calc = Calculator()
        return calc

def main():
    CalculatorApp().run()