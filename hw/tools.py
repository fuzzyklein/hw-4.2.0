from cmd import Cmd
columnize = Cmd().columnize

import re

def public(obj):
    Cmd().columnize([member for member in dir(obj) if not re.match('_', member)])

# def strout(s, )
