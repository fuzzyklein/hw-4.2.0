from cmd import Cmd
from functools import partial
import re
from subprocess import check_output

run = partial(check_output, encoding='utf-8')

columnize = Cmd().columnize

def public(obj):
    Cmd().columnize([member for member in dir(obj) if not re.match('_', member)])

# def strout(s, )
