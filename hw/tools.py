from functools import partial, wraps
import logging
import os
from pathlib import Path
from subprocess import check_output

run = partial(check_output, encoding='utf-8')

def path2str(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        args = [str(a) for a in args]
        return f(*args, **kwargs)
    return wrapper

@path2str
def invisible(f):
    for s in f.split(os.sep):
        if s.startswith('.'):
            return True
    return False

def str2path_method(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        args = [args[0], *[Path(a) for a in args[1:]]]
        return f(*args, **kwargs)
    return wrapper

class Logging():
    """ Abstract data class. Initializes its `log` variable so subclasses can
        log messages implicitly by default.
    """

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(str(type(self)))
