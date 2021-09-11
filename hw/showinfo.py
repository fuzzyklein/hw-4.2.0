from imports import *
from tools import *

from ansicolortags import printc

pyenv = {k: v for k, v in environ.items() if k.startswith('PYTHON')}
printc('<yellow>Python Environment Variables<reset>:')
pp(pyenv)
print()
print(f'{__debug__=}')
if __debug__: print("What the fuck is going on?")
