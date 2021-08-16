from cmd import Cmd
from functools import partial, wraps
from glob import glob
import re
from subprocess import check_output

run = partial(check_output, encoding='utf-8')

columnize = Cmd().columnize

def public(obj):
    Cmd().columnize([member for member in dir(obj) if not re.match('_', member)])

def globber(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        expanded_args = list()
        if args:
            for a in map(lambda s: str(s), args):
                expanded_args.extend(glob(a))
        return f(*[Path(p) for p in expanded_args], **kwargs)
    return wrapper
