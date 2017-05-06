from collections import namedtuple

PlayerContact = namedtuple('PlayerContact', ['name', 'phone'])

UIButton = namedtuple('UIButton', ['text', 'switch_inline', 'callback', 'arg'])
