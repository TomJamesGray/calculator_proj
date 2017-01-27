import logging
import re
import math
from calc.helpers import nested_in,nested_contains

#Define the special functions with lambdas
#and convert from degrees to radians
special_functions = [
    ('sin', lambda x: math.sin(math.radians(x))),
    ('cos', lambda x: math.cos(math.radians(x))),
    ('tan', lambda x: math.tan(math.radians(x))),
    ('sqrt',lambda x: math.sqrt(x))
]

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
    #Replace π with 3.14...
    calc_line = calc_line.replace("π",str(math.pi))
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
