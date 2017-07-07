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
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle,Color,Translate,Line
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
        Window.size = (700,450)
        self.clear_widgets()
        self.add_widget(GraphingCalc(pos=(0,0),width=700,height=450))

    def clear_line(self):
        self.screen.text = ""

class ColourSpinner(Spinner):
    pass

class GraphingCalc(Widget):
    function_input = ObjectProperty(None)
    function_colour_input = ObjectProperty(None)
    function_grid = ObjectProperty(None)
    max_x_input = ObjectProperty(None)
    min_x_input = ObjectProperty(None)
    max_y_input = ObjectProperty(None)
    min_y_input = ObjectProperty(None)
    x_step_input = ObjectProperty(None)
    y_step_input = ObjectProperty(None)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.x_max = 5
        self.x_min = -5
        self.x_step = 1
        self.y_max = 5
        self.y_min = -5
        self.y_step = 1
        self.graph_width = 400
        self.graph_height = 410
        self.x_label_objects = None
        self.y_label_objects = None
        self.graph = RelativeLayout(pos=(300,0),width=self.graph_width,height=self.graph_height)
        Window.bind(on_touch_up=self.graph_mouse_pos)
        Window.bind(on_touch_move=self.graph_move)
        self.function_inputs = [[self.function_input,self.function_colour_input]]
        self.colour_maps = {
            "Colour":(0,0,0,1),
            "Black":(0,0,0,1),
            "Red":(1,0,0,1),
            "Blue":(0,0,1,1)
        }

        self.initialise_graph()
        self.add_widget(self.graph)

    def initialise_graph(self):
        """
        Initialises the graph layout, works if canvas is or isn't already populated. Also resets
        the axis labels
        """
        with self.graph.canvas:
            Color(1,1,1,1)
            Rectangle(pos=(0,0),size=self.graph.size)
            Color(0,0,0,1)
            # Major Y axis
            self.generate_axes(self.carte_to_px(0, self.y_min), (1, 410), (0, 0, 0, 1))

            # Major X axis
            self.generate_axes(self.carte_to_px(self.x_min, 0), (400, 1), (0, 0, 0, 1))

            # Minor y axes
            #TODO Don't use range to allow for decimal steps, etc
            for i in range(int(self.x_min), int(self.x_max + self.x_step), int(self.x_step)):
                self.generate_axes(self.carte_to_px(i, self.y_min), (1, 410), (.1, .1, .1, .4))

            # Minor x axes
            for i in range(int(self.y_min), int(self.y_max + self.y_step), int(self.y_step)):
                self.generate_axes(self.carte_to_px(self.x_min, i), (400, 1), (.1, .1, .1, .4))

            # If labels already exist remove them (incase limits have changed)
            if self.x_label_objects != None:
                for lbl in self.x_label_objects:
                    lbl.clear_widgets()

                for lbl in self.y_label_objects:
                    lbl.clear_widgets()

            self.x_label_objects = []
            self.y_label_objects = []

            # Add x labels
            x_labels = list(range(int(self.x_min),int(self.x_max+self.x_step),int(self.x_step)))
            x_spacing = self.graph_width/len(x_labels)

            for i,lbl in enumerate(x_labels):
                x,y = self.carte_to_px(x_labels[i], 0)
                # Check if label would go outside canvas
                if x < 0 or y+10 > self.graph_height:
                    continue
                a = Label(pos=(x,y), font_size="8sp", width=7, height=10,
                          color=(0, 0, 0, 1), text=str(x_labels[i]))
                self.x_label_objects.append(a)

            # Add y labels
            y_labels = list(range(int(self.y_min), int(self.y_max + self.y_step), int(self.y_step)))
            y_spacing = self.graph_height / len(y_labels)

            for i, lbl in enumerate(y_labels):
                x, y = self.carte_to_px(0,y_labels[i])
                # Check if label would go outside canvas
                if x < 0 or y+10 > self.graph_height:
                    continue
                # Don't repeat 0 as already done on x label run
                if y_labels[i] == 0:
                    continue
                a = Label(pos=self.carte_to_px(0,y_labels[i]), font_size="8sp", width=7, height=10,
                          color=(0, 0, 0, 1), text=str(y_labels[i]))
                self.y_label_objects.append(a)

            Translate(xy=self.pos)

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

    def px_to_carte(self,px_x,px_y):
        """
        Converts a given pixel co-ordinate into the coresponding cartesian co-ordinate
        :param px_x: X value for co-oridnatea
        :param px_y: Y value for co-ordinate
        :return:
        """
        prop_x = px_x/self.graph_width
        prop_y = px_y/self.graph_height
        return (prop_x*(self.x_max-self.x_min)+self.x_min,prop_y*(self.y_max-self.y_min)+self.y_min)

    def graph_move(self,*args):
        print("---")
        dx = -int(args[1].dx)
        dy = -int(args[1].dy)
        dx_carte,dy_carte = self.px_to_carte(dx,dy)
        dx_carte = dx_carte-self.x_min
        dy_carte = dy_carte-self.y_min
        print("Graph move event dx: {}, dy: {} (px)\ndx: {}, dy:{} (carte)".format(dx,dy,dx_carte,dy_carte))
        self.y_min = self.y_min + dy_carte
        self.y_max = self.y_max + dy_carte
        self.x_min = self.x_min + dx_carte
        self.x_max = self.x_max + dx_carte
        print("x min: {}, x max: {}\ny min: {},y max:{}".format(self.x_min,self.x_max,self.y_min,self.y_max))
        self.initialise_graph()
        self.graph_it()

    def graph_mouse_pos(self,*args):
        """
        Checks if the mouse is over the graph canvas then zooms in/out if scroll whell is used
        :param args:
        :return:
        """
        x_px = int(args[1].pos[0])
        y_px = int(args[1].pos[1])
        if self.graph.collide_point(x_px,y_px):
            btn = args[1].button
            if btn == "scrollup":
                zoom_factor = 1.05
            elif btn == "scrolldown":
                zoom_factor = 0.95
            else:
                return False
            self.x_max *= zoom_factor
            self.x_min *= zoom_factor
            self.y_max *= zoom_factor
            self.y_min *= zoom_factor
            self.initialise_graph()
            self.graph_it()

    def generate_axes(self,pos,size,col):
        # Check axis won't go outside of canvas
        if pos[0] < 0 or pos[1] > self.graph_height:
            return False
        with self.graph.canvas:
            Color(*col)
            Rectangle(pos=pos,size=size)
            # Translate(xy=self.pos)

    def graph_it(self,ignore_lims=False):
        with self.graph.canvas:
            if ignore_lims:
                # Update x,y maxes and mins and step
                self.x_min = float(self.min_x_input.text)
                self.x_max = float(self.max_x_input.text)
                self.y_min = float(self.min_y_input.text)
                self.y_max = float(self.max_y_input.text)
                self.x_step = float(self.x_step_input.text)
                self.y_step = float(self.y_step_input.text)
                # Re-initialise graph
                self.initialise_graph()

            # Graph each function in function_inputs
            for func in self.function_inputs:
                func_col = self.colour_maps[func[1].text]
                prev_x = None
                prev_y = None
                for px_x in range(0, self.graph_width):
                    carte_x = self.px_to_carte(px_x, 0)[0]
                    carte_y = calculations.parse_line(func[0].text.replace("x",str(carte_x)))

                    if prev_x == None:
                        prev_x = carte_x
                        prev_y = carte_y
                    else:
                        Color(*func_col)
                        px_x,px_y = self.carte_to_px(carte_x,carte_y)

                        if px_y > self.graph_height or px_y < 0:
                            # Point goes outside canvas so don't graph it and reset prev_x and prev_y
                            prev_x = None
                            prev_y = None
                            continue

                        Line(points=[px_x,px_y, *self.carte_to_px(prev_x, prev_y)], width=1.01)
                        prev_x = carte_x
                        prev_y = carte_y
                Translate(xy=self.pos)

    def add_function(self):
        self.function_grid.add_widget(Label(text="y = "))
        new_input = TextInput(write_tab=False)
        new_col_input = ColourSpinner()
        self.function_inputs.append([new_input,new_col_input])
        self.function_grid.add_widget(new_input)
        self.function_grid.add_widget(new_col_input)

class CalculatorApp(App):
    def build(self):
        self.title = "Calculator"
        Window.size=(350,450)
        calc = Calculator()
        return calc

def main():
    CalculatorApp().run()