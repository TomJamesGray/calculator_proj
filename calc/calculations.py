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
        "level":2,
        "regex_name":"\+"
    },
    "-":{
        "n":2,
        "func": lambda x,y: x-y,
        "level":2,
        "regex_name":"-"
    },
    "*":{
        "n":2,
        "func":lambda x,y: x*y,
        "level":3,
        "regex_name":"\*"
    },
    "/":{
        "n":2,
        "func":lambda x,y:x/y,
        "level":3,
        "regex_name":"\/"
    },
    "^":{
        "n":2,
        "func":lambda x,y:x**y,
        "level":4,
        "regex_name":"\^"
    },
    "(":{
        "n":0,
        "func":None,
        "level":1,
        "regex_name":"\("
    },
    ")":{
        "n":0,
        "func":None,
        "level":1,
        "regex_name":"\)"
    },
    "sin":{
        "n":1,
        "func":lambda x:math.sin(x),
        "level":5,
        "regex_name":"sin"
    },
    "cos": {
        "n": 1,
        "func": lambda x: math.cos(x),
        "level": 5,
        "regex_name": "cos"
    },
    "tan": {
        "n": 1,
        "func": lambda x: math.tan(x),
        "level": 5,
        "regex_name": "tan"
    }
}

logger = logging.getLogger(__name__)

def parse_line(calc_line,ans=None):
    """
    Parses a given equation by converting infix to reverse polish
    :param calc_line: The equation
    :param prev_ans: The value for ANS if it appears in the calc_line, defaults to None
    :return:
    """
    global functions
    f_stack = []
    rpn_line = []
    # Construct regex to split on all operations
    regex_names = []
    for f_name,func in functions.items():
        regex_names.append(func["regex_name"])

    f_line = re.split("({})".format("|".join(regex_names)),calc_line)

    logger.info("Eval {}".format(f_line))

    for c in f_line:
        if c == "":
            continue
        logger.debug("Using {}".format(c))
        if c in functions:
            # Current item is a function
            if c == "(":
                logger.debug("Adding ( to f_stack")
                f_stack.append(c)
            elif c == ")":
                logger.debug("Closing bracket")
                while f_stack[-1] != "(":
                    rpn_line.append(f_stack.pop())
                f_stack.pop()
                logger.debug("f_stack after ')': {}".format(f_stack))

            elif len(f_stack) == 0:
                logger.debug("Appending function {} to empty f_stack".format(c))
                f_stack.append(c)
            elif functions[f_stack[-1]]["level"] < functions[c]["level"]:
                logger.debug("Appending function {} to f_stack".format(c))
                f_stack.append(c)
            else:
                try:
                    while functions[f_stack[-1]]["level"] >= functions[c]["level"]:
                        logger.debug("Adding {} to rpn_line as higher than {}".format(f_stack[-1],c))
                        rpn_line.append(f_stack.pop())
                except IndexError:
                    # f_stack is empty
                    pass
                f_stack.append(c)
                logger.debug("Added {} to f_stack, now {}".format(c,f_stack))
            logger.debug("f_stack at {}".format(f_stack))

        else:
            # Current item is an operand
            rpn_line.append(c)

    while f_stack != []:
        rpn_line.append(f_stack.pop())

    logger.info("RPN line at end of parsing: {}".format(rpn_line))
    val = eval_rpn(rpn_line)
    return val

def eval_rpn(rpn_line):
    global functions
    eval_stack = []
    for c in rpn_line:
        if c in functions:
            logger.debug("Evaluating function {}".format(c))
            func = functions[c]
            args = []
            for i in range(0,func["n"]):
                # Retrieve required amount of arguments
                args.append(float(eval_stack.pop()))
            # Reverse args so first argument would be towards bottom of stack
            args = args[::-1]
            logger.debug("Using args: {}".format(args))
            val = func["func"](*args)
            eval_stack.append(val)
            logger.debug("Adding value from function {} to stack".format(val))
        else:
            logger.debug("Adding {} to eval_stack".format(c))
            eval_stack.append(c)
            logger.debug("eval_stack at {}".format(eval_stack))

    return eval_stack[0]