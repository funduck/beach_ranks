from collections import namedtuple

Button = namedtuple('Button', ['text', 'switch_inline', 'callback'])

def ifNone(val, default_val):
    if val is None:
        return default_val
    else:
        return val
