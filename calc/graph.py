from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle,Color,Translate,Line
from kivy.clock import Clock
from calc import calculations
from calc.helpers import float_range,float_round

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
        self.x_grid_step = 1
        self.x_label_step = 1
        self.y_max = 5
        self.y_min = -5
        self.y_grid_step = 1
        self.y_label_step = 1
        self.graph_width = 400
        self.graph_height = 410
        self.x_label_objects = None
        self.y_label_objects = None
        self.graph_it_loop = None
        self.graph = RelativeLayout(pos=(300,0),width=self.graph_width,height=self.graph_height)
        Window.bind(on_touch_up=self.graph_mouse_pos)
        Window.bind(on_touch_move=self.graph_move)
        self.function_inputs = [[self.function_input,self.function_colour_input]]
        self.anim_vars = []
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
            for i in float_range(float_round(self.x_min,self.x_grid_step),
                                 float_round(self.x_max + self.x_grid_step,self.x_grid_step), self.x_grid_step):
                self.generate_axes(self.carte_to_px(i, self.y_min), (1, 410), (.1, .1, .1, .4))

            # Minor x axes
            for i in float_range(float_round(self.y_min, self.y_grid_step),
                                 float_round(self.y_max + self.y_grid_step, self.y_grid_step), self.y_grid_step):
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
            x_labels = list(range(int(self.x_min),int(self.x_max+self.x_label_step),self.x_label_step))
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
            y_labels = list(range(int(self.y_min), int(self.y_max + self.y_label_step), self.y_label_step))
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
        dx = -int(args[1].dx)
        dy = -int(args[1].dy)
        dx_carte,dy_carte = self.px_to_carte(dx,dy)
        dx_carte = dx_carte-self.x_min
        dy_carte = dy_carte-self.y_min
        # print("Graph move event dx: {}, dy: {} (px)\ndx: {}, dy:{} (carte)".format(dx,dy,dx_carte,dy_carte))
        self.y_min = self.y_min + dy_carte
        self.y_max = self.y_max + dy_carte
        self.x_min = self.x_min + dx_carte
        self.x_max = self.x_max + dx_carte
        # print("x min: {}, x max: {}\ny min: {},y max:{}".format(self.x_min,self.x_max,self.y_min,self.y_max))
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

    def pause_play(self,btn):
        if self.graph_it_loop == None:
            # Start animated vars
            if self.anim_vars != []:
                for var in self.anim_vars:
                    var.disabled = False
                self.graph_it_loop = Clock.schedule_interval(self.graph_it, 0.1)
            btn.text = "Pause"
        else:
            # Stop animated vars
            self.graph_it_loop.cancel()
            # Disable all anim vars
            if self.anim_vars != []:
                for var in self.anim_vars:
                    var.disabled = True
            self.graph_it_loop = None
            btn.text = "Play"

    def generate_axes(self,pos,size,col):
        # Check axis won't go outside of canvas
        if pos[0] < 0 or pos[1] > self.graph_height:
            return False
        with self.graph.canvas:
            Color(*col)
            Rectangle(pos=pos,size=size)
            # Translate(xy=self.pos)

    def graph_it_btn(self):
        Clock.schedule_interval(self.graph_it, 1)

    def graph_it(self,reinitialse=False):
        with self.graph.canvas:
            # if ignore_lims:
            #     # Update x,y maxes and mins and step
            #     self.x_min = float(self.min_x_input.text)
            #     self.x_max = float(self.max_x_input.text)
            #     self.y_min = float(self.min_y_input.text)
            #     self.y_max = float(self.max_y_input.text)
            #     self.x_step = float(self.x_step_input.text)
            #     self.y_step = float(self.y_step_input.text)
            #     # Re-initialise graph
            #     self.initialise_graph()
            if reinitialse:
                self.initialise_graph()
            # Step over any anim_vars
            cur_anim_vars = []
            if self.anim_vars != []:
                for var in self.anim_vars:
                    x = var.step()
                    cur_anim_vars.append({"name":var.name_in.text,"val":x})

            # Graph each function in function_inputs
            for func in self.function_inputs:
                f_line = func[0].text
                func_col = self.colour_maps[func[1].text]
                prev_x = None
                prev_y = None

                # Insert any anim vars
                if self.anim_vars != []:
                    for var in cur_anim_vars:
                        f_line = f_line.replace(var["name"], str(var["val"]))

                for px_x in range(0, self.graph_width,2):
                    carte_x = self.px_to_carte(px_x, 0)[0]
                    try:
                        carte_y = calculations.parse_line(f_line.replace("x",str(carte_x)))
                    except Exception:
                        prev_x = None
                        prev_y = None
                        continue

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
                        else:
                            Line(points=[px_x,px_y, *self.carte_to_px(prev_x, prev_y)], width=1.01)
                            prev_x = carte_x
                            prev_y = carte_y
                Translate(xy=self.pos)

    def add_function(self):
        container = GridLayout(row_default_height=30,row_force_default=True,cols_minimum={0:45,1:145,2:95},cols=3,
                               spacing=(5,5))
        container.add_widget(Label(text="y = "))
        new_input = TextInput(write_tab=False)
        new_col_input = ColourSpinner()
        self.function_inputs.append([new_input,new_col_input])
        container.add_widget(new_input)
        container.add_widget(new_col_input)
        self.function_grid.add_widget(container)

    def add_anim_var(self):
        container = GridLayout(cols=8)
        name = TextInput(write_tab=False,font_size="10sp")
        min = TextInput(write_tab=False,font_size="10sp")
        max = TextInput(write_tab=False,font_size="10sp")
        step = TextInput(write_tab=False,font_size="10sp")
        self.anim_vars.append(AnimVar(name,min,max,step))
        # for i,x in enumerate(["Name","Min","Max","Step"]):

        container.add_widget(Label(font_size="10sp",text="Name"))
        container.add_widget(name)
        container.add_widget(Label(font_size="10sp", text="Min"))
        container.add_widget(min)
        container.add_widget(Label(font_size="10sp", text="Max"))
        container.add_widget(max)
        container.add_widget(Label(font_size="10sp", text="Step"))
        container.add_widget(step)

        self.function_grid.add_widget(container)

class AnimVar(object):
    def __init__(self,name_in,min_in,max_in,step_in):
        self.name_in = name_in
        self.min_in = min_in
        self.max_in = max_in
        self.step_in = step_in
        self.current = None
        self.disabled = True

    def step(self):
        if self.current == None:
            self.current = float(self.min_in.text)

        if self.disabled:
            return self.current

        if self.current + float(self.step_in.text) > float(self.max_in.text):
            self.current = float(self.min_in.text)
        else:
            self.current += float(self.step_in.text)

        return self.current