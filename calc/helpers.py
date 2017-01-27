
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

