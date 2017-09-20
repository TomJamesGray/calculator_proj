import logging
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle,Color,Translate,Ellipse,Line
from kivy.clock import Clock
from calc import calculations
from calc.helpers import float_range,float_round

logger = logging.getLogger(__name__)

class ColourSpinner(Spinner):
    pass

class GraphingCalc(Widget):
    function_input = ObjectProperty(None)
    function_colour_input = ObjectProperty(None)
    function_grid = ObjectProperty(None)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        logger.info("Initialising Graphing calc")
        self.width = 900
        self.x_max = 5
        self.x_min = -5
        self.x_grid_step = 1
        self.x_label_step = 1
        self.y_max = 5
        self.y_min = -5
        self.y_grid_step = 1
        self.y_label_step = 1
        self.graph_width = 540
        self.graph_height = 410
        self.x_label_objects = None
        self.y_label_objects = None
        self.graph_it_loop = None
        self.point_show = None
        self.popup_active = False
        self.cords = []
        self.graph = RelativeLayout(pos=(340,0),width=self.graph_width,height=self.graph_height)
        Window.bind(on_touch_down=self.graph_mouse_pos)
        Window.bind(on_touch_up=self.remove_point_show)
        Window.bind(on_touch_move=self.graph_move)
        Window.bind(on_resize=self.resize)
        # self.function_inputs = [[self.function_input,self.function_colour_input]]
        self.function_inputs = []
        self.add_function()
        self.anim_vars = []
        self.colour_maps = {
            "Colour":(0,0,0,1),
            "Black":(0,0,0,1),
            "Red":(1,0,0,1),
            "Blue":(0,0,1,1)
        }

        self.initialise_graph()
        self.add_widget(self.graph)

    def resize(self,*args):
        new_width = args[1]
        self.width = new_width
        new_height = args[2]
        self.height = new_height
        logger.info("Resizing graphing calc, new width: {}, new_height: {}".format(new_width,new_height))

        self.graph_width = new_width-300
        self.graph_height = new_height-40
        self.graph.width = self.graph_width
        self.graph.height = self.graph_height
        self.graph_it(True)

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
            self.generate_axes(self.carte_to_px(0, self.y_min), (1, self.graph_height), (0, 0, 0, 1))

            # Major X axis
            self.generate_axes(self.carte_to_px(self.x_min, 0), (self.graph_width, 1), (0, 0, 0, 1))

            # Minor y axes
            for i in float_range(float_round(self.x_min,self.x_grid_step),
                                 float_round(self.x_max + self.x_grid_step,self.x_grid_step), self.x_grid_step):
                self.generate_axes(self.carte_to_px(i, self.y_min), (1, self.graph_height), (.1, .1, .1, .4))

            # Minor x axes
            for i in float_range(float_round(self.y_min, self.y_grid_step),
                                 float_round(self.y_max + self.y_grid_step, self.y_grid_step), self.y_grid_step):
                self.generate_axes(self.carte_to_px(self.x_min, i), (self.graph_width, 1), (.1, .1, .1, .4))

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
        if not self.popup_active:
            btn = args[1].button
            if btn == "left" and isinstance(self.point_show,ShowPoint):
                # Move point show
                x_px = args[1].x-self.graph.pos[0]
                logger.info("Moving co-ordinate point to x px = {} on graph".format(x_px))
                self.point_show.move_x(x_px)
            else:
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
                # self.update_lims()
                self.initialise_graph()
                self.graph_it()

    def remove_point_show(self,*args):
        if self.point_show != None:
            self.remove_widget(self.point_show)
            self.point_show = None

    def graph_mouse_pos(self,*args):
        """
        Checks if the mouse is over the graph canvas then zooms in/out if scroll whell is used
        :param args:
        :return:
        """
        if not self.popup_active:
            x_px = int(args[1].pos[0])
            y_px = int(args[1].pos[1])
            if self.graph.collide_point(x_px,y_px):
                btn = args[1].button
                if btn == "scrollup":
                    zoom_factor = 1.05
                elif btn == "scrolldown":
                    zoom_factor = 0.95
                elif btn == "left":
                    # Don't plot points if graph is currently playing with anim vars
                    graph_x_px = x_px-self.graph.pos[0]
                    graph_y_px = y_px-self.graph.pos[1]
                    logger.info("Press at: {} {}".format(graph_x_px,graph_y_px))
                    # Loop through cords
                    cur_min_delta = 6
                    cur_optimum_point = None
                    cur_function = None
                    for f_no,set in enumerate(self.cords):
                        for i in range(0,len(set),2):
                            x = set[i]
                            y = set[i+1]
                            delta = ((graph_x_px-x)**2+(graph_y_px-y)**2)**0.5
                            if delta < 5 and delta < cur_min_delta:
                                cur_optimum_point = (x,y)
                                cur_min_delta = delta
                                cur_function = f_no
                                #Within 5 px radius
                                logger.info("New optimum point: {}".format(cur_optimum_point))

                    if cur_optimum_point != None:
                        self.point_show = ShowPoint(self,cur_optimum_point,self.function_inputs[cur_function][0].text)
                        self.add_widget(self.point_show)

                    return True
                else:
                    return False

                self.x_max *= zoom_factor
                self.x_min *= zoom_factor
                self.y_max *= zoom_factor
                self.y_min *= zoom_factor
                # self.update_lims()
                self.initialise_graph()
                self.graph_it()

    def update_lims(self,x_min,x_max,y_min,y_max,x_step,y_step):
        """
        Updates the values for the min, max and step text inputs for x and y
        """
        # self.a.dismiss()
        # logger.info("I")
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        self.x_grid_step = float(x_step)
        self.y_grid_step = float(y_step)
        self.initialise_graph()
        self.graph_it()

    def pause_play(self,btn):
        if self.graph_it_loop == None:
            # Start animated vars
            if self.anim_vars != []:
                logger.info("Enabling animated variables")
                for var in self.anim_vars:
                    var.disabled = False
                self.graph_it_loop = Clock.schedule_interval(lambda x: self.graph_it(True,True), 0.1)
                btn.text = "Pause"
        else:
            logger.info("Disabling animated variables")
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

    def insert_anim_vars(self,f_line,step=True):
        """
        Inserts and by default steps over any anim vars
        :param f_line: The function line to be modified and evaluated
        :param step: Whether to step over the anim vars, defaults to True
        :return: Modified function line with anim vars
        """
        # Step over any anim_vars
        cur_anim_vars = []
        if self.anim_vars != []:
            for var in self.anim_vars:
                if step:
                    x = var.step()
                else:
                    x = var.current
                cur_anim_vars.append({"name": var.name_in.text, "val": x})

        # Insert any anim vars
        if self.anim_vars != []:
            for var in cur_anim_vars:
                f_line = f_line.replace(var["name"], str(var["val"]))

        return f_line


    def graph_it(self,reinitialse=False,update_point_show=False):
        self.cords = []
        with self.graph.canvas:
            if reinitialse:
                self.graph.canvas.clear()
                self.initialise_graph()
            if update_point_show and self.point_show != None:
                logger.info("Updating point show")
                self.point_show.update()

            # Graph each function in function_inputs
            for func in self.function_inputs:
                f_line = self.insert_anim_vars(func[0].text)
                func_col = self.colour_maps[func[1].text]
                func_cords = []
                points = []
                cur_seg = []

                for px_x in range(0, self.graph_width,2):
                    set_none = False
                    # ignore_next = False
                    carte_x = self.px_to_carte(px_x, 0)[0]
                    try:
                        carte_y = calculations.parse_line(f_line.replace("x",str(carte_x)))
                    except Exception:
                        prev_x = None
                        prev_y = None
                        continue

                    px_x, px_y = self.carte_to_px(carte_x,carte_y)
                    px_y = round(px_y)
                    if px_y > self.graph_height:
                        px_y = self.graph_height
                        cur_seg.append(px_x)
                        cur_seg.append(px_y)
                        points.append(cur_seg)
                        cur_seg = []
                    elif px_y < 0:
                        px_y = 0
                        cur_seg.append(px_x)
                        cur_seg.append(px_y)
                        points.append(cur_seg)
                        cur_seg = []
                    else:
                        if len(cur_seg) == 0:
                            # If the cur_seg will just be a point, try and connect it to top/bottom of screen
                            try:
                                cur_seg.append(points[-1][0])
                                cur_seg.append(points[-1][1])
                            except IndexError:
                                pass

                        cur_seg.append(px_x)
                        cur_seg.append(px_y)

                points.append(cur_seg)
                Color(*func_col)
                for seg in points:
                    [func_cords.append(x) for x in seg]
                    Line(points=seg,width=1.01)

                self.cords.append(func_cords)


                Translate(xy=self.pos)

    def add_function(self):
        container = GridLayout(row_default_height=30,row_force_default=True,cols_minimum={0:40,1:190,2:95},cols=3,
                               spacing=(5,5))
        new_input = TextInput(write_tab=False)
        new_col_input = ColourSpinner()
        delete_func = Button(text="Del")
        self.function_inputs.append([new_input,new_col_input])
        container.add_widget(delete_func)
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

    def adjust_axes_btn(self):
        self.popup_active = True
        LimitsPopup(self).open()
        # self.a = x

class LimitsPopup(Popup):
    max_x_input = ObjectProperty(None)
    min_x_input = ObjectProperty(None)
    max_y_input = ObjectProperty(None)
    min_y_input = ObjectProperty(None)
    x_step_input = ObjectProperty(None)
    y_step_input = ObjectProperty(None)

    def __init__(self,graph,**kwargs):
        super(LimitsPopup,self).__init__(**kwargs)
        self.graph = graph

    def update(self):
        logger.info("Updating limits from popup")
        # self.dismiss()
        # self.dismiss()
        self.dismiss()
        self.graph.popup_active = False
        self.graph.update_lims(self.min_x_input.text, self.max_x_input.text, self.min_y_input.text,
                                self.max_y_input.text, self.x_step_input.text, self.y_step_input.text)

class ShowPoint(Widget):
    def __init__(self,graph,point_px,func_line,**kwargs):
        self.graph = graph
        self.func_line = func_line
        self.x_px = point_px[0]
        logger.info("Initial x_px: {}".format(self.x_px))
        super(ShowPoint,self).__init__(**kwargs)
        with self.canvas:
            Color(213 / 255, 78 / 255, 160 / 255, 1)
            # Line(circle=(cur_optimum_point[0],cur_optimum_point[1],3))
            point_x = point_px[0] - 5
            point_y = point_px[1] - 5
            carte_x, carte_y = self.graph.px_to_carte(*point_px)

            abs_point_x = point_x + 340
            abs_point_y = point_y

            self.point = Ellipse(pos=(abs_point_x, abs_point_y), size=(10, 10))
            self.lbl = Label(text="({}, {})".format(round(carte_x, 2), round(carte_y, 2)),
                        pos=(abs_point_x,abs_point_y), color=(0, 0, 0, 1), height=20)

    def move_x(self,x):
        """
        Moves the position of the show point widget on the graph
        :param x: The x value of the co-ordinates of the new point on the graph
        """
        logger.info("Moving x to x_px (on canvas) to {}:".format(x))
        new_x_carte = self.graph.px_to_carte(x,0)[0]

        # Insert any anim vars wihout stepping over them and replace x
        f_line_evaluate = self.graph.insert_anim_vars(self.func_line.replace("x", str(new_x_carte)), False)
        new_y_carte = calculations.parse_line(f_line_evaluate)

        logger.info("New cartesian co-ords: {} {}".format(new_x_carte,new_y_carte))
        x_px,y_px = self.graph.carte_to_px(new_x_carte,new_y_carte)

        self.point.pos = (x_px-5+340,y_px-5)
        self.lbl.text = "({}, {})".format(round(new_x_carte,2),round(new_y_carte,2))
        self.lbl.pos = (x_px+340,y_px)

    def update(self):
        logger.info("Updating point show at x={}".format(self.x_px))
        self.move_x(self.x_px)


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