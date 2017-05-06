from collections import namedtuple

Contact = namedtuple('Contact', ['name', 'phone'])

Button = namedtuple('Button', ['text', 'switch_inline', 'callback'])
