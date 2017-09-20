
def nested_in(tuple_list,search_for,i=0):
    """
    Look in list of tuples for string at a specific index(default 0)
    returns the tuple if string is found and false if not
    """
    for t in tuple_list:
        if search_for in t:
            return t
    return False

def nested_contains(tuple_list,lookup,i=0):
    for t in tuple_list:
        if t[i] in lookup:
            return True

    return False

def float_range(low,high,step):
    i = low
    while i < high:
        yield i
        i += step

def float_round(x,nearest):
    return round(x/nearest)*nearest


# Float to string to avoid scientific notation from Karin
# https://stackoverflow.com/questions/38847690/convert-float-to-string-without-scientific-notation-and-false-precision
def float_to_str(f):
    float_string = repr(f)
    if 'e' in float_string:  # detect scientific notation
        digits, exp = float_string.split('e')
        digits = digits.replace('.', '').replace('-', '')
        exp = int(exp)
        zero_padding = '0' * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = '-' if f < 0 else ''
        if exp > 0:
            float_string = '{}{}{}.0'.format(sign, digits, zero_padding)
        else:
            float_string = '{}0.{}{}'.format(sign, zero_padding, digits)
    return float_string