import logging
import re
import math
from calc.helpers import nested_in,nested_contains

# Define the special functions with lambdas

special_functions = [
    ('sin', lambda x: math.sin(x)),
    ('cos', lambda x: math.cos(x)),
    ('tan', lambda x: math.tan(x)),
    ('sqrt',lambda x: math.sqrt(x))
]

functions = {
    "+":{
        "n":2,
        "func": lambda x,y: x+y,
        "level":2
    },
    "-":{
        "n":2,
        "func": lambda x,y: x-y,
        "level":2
    },
    "*":{
        "n":2,
        "func":lambda x,y: x*y,
        "level":3
    },
    "/":{
        "n":2,
        "func":lambda x,y:x/y,
        "level":3
    },
    "^":{
        "n":2,
        "func":lambda x,y:x**y,
        "level":4
    }
}

logger = logging.getLogger(__name__)

def parse_line(calc_line,ans):
    """
    Parses a given equation by converting infix to reverse polish
    :param calc_line: The equation
    :param prev_ans: The value for ANS if it appears in the calc_line, defaults to None
    :return:
    """
    global functions
    f_stack = []
    rpn_line = ""
    logger.info("Eval {}".format(calc_line))
    for c in calc_line[0]:
        logger.debug("Using {}".format(c))
        if c in functions:
            # Current character is a function
            if len(f_stack) == 0:
                logger.debug("Appending function {} to empty f_stack".format(c))
                f_stack.append(c)
            elif functions[f_stack[-1]]["level"] < functions[c]["level"]:
                logger.debug("Appending function {} to f_stack".format(c))
                f_stack.append(c)
            else:
                while functions[f_stack[-1]]["level"] >= functions[c]["level"]:
                    logger.debug("Adding {} to rpn_line as higher than {}".format(f_stack[-1],c))
                    rpn_line += f_stack.pop()
                f_stack.append(c)
                logger.debug("Added {} to f_stack, now {}".format(c,f_stack))

        else:
            # Current character is an operand
            rpn_line += c


    while f_stack != []:
        rpn_line += f_stack.pop()

    logger.info("RPN line at end of parsing: {}".format(rpn_line))
    return 5