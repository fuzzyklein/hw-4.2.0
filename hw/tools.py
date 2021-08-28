from cmd import Cmd
from configparser import ConfigParser
from enum import IntEnum
from ftplib import FTP
from functools import partial, singledispatch, wraps
from glob import glob
from io import StringIO
import os
from os import chdir as cd
from pathlib import Path
from pprint import pprint as pp
import re
from shutil import copy2 as cp
from subprocess import check_output
from traceback import print_exc
from warnings import warn

from bs4 import BeautifulSoup

import files

BASEDIR = Path(__file__).parent.parent

columnize = Cmd().columnize
run = partial(check_output, encoding='utf-8')

def public(obj):
    Cmd().columnize([member for member in dir(obj) if not re.match('_', member)])

def globber(f):
    DEBUG = False
    @wraps(f)
    def wrapper(*args, **kwargs):
        if DEBUG:
            print()
            print('Debugging `globber.wrapper`')
            print()
            print('Arguments:')
            print()
            pp(args)
            print()
        expanded_args = list()
        if args:
            for a in map(lambda s: str(s), args):
                expanded_args.extend(glob(a))
        if DEBUG:
            print("Expanded Arguments:")
            print()
            pp(expanded_args)
            print()
        return f(*[Path(p) for p in expanded_args], **kwargs)
    return wrapper

@globber
def configure(p=BASEDIR/'etc'/'config.ini'):
    DEBUG = False
    cnf = ConfigParser()
    if DEBUG:
        print(f'Getting configuration from file {str(p)}')
    cnf.read(str(p))
    return cnf

def get_file_from_server(s:str):
    env = configure()['ENVIRONMENT']
    ftp = FTP(env['server_ip'])
    ftp.login('russell', (Path.home() / env['ftp_pass']).read_text())
    p = Path(s)
    dir = str(p.parent)
    ftp.cwd(dir)
    ftp.retrlines(f'RETR {p.name}')
    ftp.close()

def exists(ftp, s):
    cur_dir = ftp.pwd()
    try:
        ftp.cwd(s)
        ftp.cwd(cur_dir)
        return True
    except ftplib.error_perm as e:
        print(e)
        lastresp = ftp.lastresp
        ftp.cwd(cur_dir)
        try:
            ftp.size(s)
            # ftp.cwd(cur_dir)
            return True
        except ftplib.error_perm as e:
            print(e)
            # ftp.cwd(cur_dir)
            return False
        # return False
    ftp.cwd(cur_dir)

def make_remote_dirs(ftp, s):
    components = s.split(os.sep)
    i = -1
    pp(components)
    s0 = os.sep.join(components[:i])
    print(s0)
    while len(s0) and not exists(ftp, s0):
         print(f'Directory {s0} does not exist.')
         i -= 1
         s0 = os.sep.join(components[:i])
         print(f'Next directory to check: {s0}')
    print(len(s0))
    while i < 0:
        i += 1
        s0 = os.sep.join(components[:i])
        if len(s0):
            print(f'Making directory {s0}')
            ftp.mkd(s0)

def login():
    password = (Path.home() / conf['ftp_pass']).read_text()
    ftp = FTP(conf['server_ip'])
    ftp.login('russell', password)
    return ftp

@globber
def cat(*args, **kwargs):
    """Return a string containing the concatenation of any files given as `args`."""
    s = str()
    for f in args:
        if not f.exists():
            warn(f'File {f.name} does not exist.')
        else:
            try:
                s += f.read_text()
            except FileNotFoundError:
                warn(f'File {str(f)} not found!')
    if not 'quiet' in kwargs.keys() or kwargs['quiet'] == False: print(s)
    return s

@singledispatch
def pdf2txt(x, **kwargs):
    raise NotImplementedError("first arg to `pdf2txt` must be `str` or `Path`")


@pdf2txt.register
def _(p:Path, **kwargs):
    return pdf2txt(str(p), **kwargs)

@pdf2txt.register
def _(s:str, **kwargs):
    """Retrieve the text of a PDF file by calling `pdf2txt.py`."""
    s = run(['pdf2txt.py', str(p)])
    if 'lines' in kwargs.keys() and kwargs['lines']:
        s = s.split('\n')
    return s

def flatten(L:list):
    """ Return a list comprising all the elements of any list within the list.
        Also include any non-list elements of the argument list.
    """
    retval = list()
    for l in L:
        if issubclass(type(l), list):
            retval.extend(l)
        else:
            retval.append(l)
    return retval

@globber
def slurp(*args, **kwargs):
    """ Open a file(s), read all of its text, and return the result.
    """
    return cat(*args, **kwargs).split('\n')

@globber
def grep(*args, **kwargs):
    DEBUG = True
    if DEBUG: print('Debugging `grep().')
    retval = list()
    lines = slurp(*args, **kwargs)
    if not 'pattern' in kwargs.keys():
        print('`grep()` function requires a pattern.')
        return None
    else:
        pattern = kwargs['pattern']
        if DEBUG:
            print(f'{type(pattern)=}')
        if not type(pattern) is list:
            pattern = [pattern]
        for pat in pattern:
            print(f'Processing pattern {pat}')
            if not type(pat) is re.Pattern:
                pat = re.compile(pat)
            retval.extend([line for line in lines if pat.match(line)])
    return retval

def pwd(quiet=False):
    value = Path(os.curdir).absolute()
    if not quiet: print(str(value))
    return value

cwd = partial(pwd, quiet=True)

def csv2html(path=None, code=False):
    """ Read a (specially designed) CSV file and return it as HTML.

        TODO: Handle the first row specially and optionally.
    """
    if type(path) is str:
        path = Path(path)
    with path.open() as f:
        reader = csv.reader(f)
        output = '<table>'
        for i, row in enumerate(reader):
            if code:
                row[0] = "<code>" + row[0] + "</code>"
            output+=('<tr><td>{}</td></tr>\n'
                  .format("</td><td>".join(row)))
        output+=("</table>\n")

        # print( output)
        return output

def get_all(path, ignore=set()):
    """ Get the names of all the variables, classes and functions defined within
        a module.
    """
    result = set()
    if type(path) is str:
        path = Path(path)
    lines = path.read_text().split('\n')
    regex = re.compile("def (\w*)|class (\w*)|(\w*)\s+=")
    for s in lines:
        m = regex.match(s)
        if m:
            i = 1
            while not m.group(i):
                i += 1
            assert i < 4
            word = m.group(i)
            if word and not word.startswith('_'):
                result.add(word)
    return sorted(list(result.difference(ignore)))

def str2path(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        args = [Path(a) for a in args]
        return f(*args, **kwargs)
    return wrapper

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

class BS(BeautifulSoup):
    def __init__(self, s):
        super().__init__(s, features="html.parser")

START_COLOR_CODE = '\033['
END_COLOR_CODE = '\033[0m'

class FG_COLORS(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97

class BG_COLORS(IntEnum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97


def color_str(s, style=1, fg=FG_COLORS.BLACK, bg=BG_COLORS.BLACK):
    return START_COLOR_CODE + f'{style};{fg};{bg}m{s}' + END_COLOR_CODE

def str2list(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*[s.split() for s in args], **kwargs)
    return wrapper

@str2list
def sh(s):
    if '|' in s:
        raise Exception("Pipes don't work in system calls worth a damn!")
    return run(s)

__all__ = [ 'cd', 'pp', 'columnize', 'run', 'public', 'globber', 'configure',
            'get_file_from_server', 'exists', 'make_remote_dirs', 'login',
            'cat', 'pdf2txt', 'flatten', 'slurp', 'grep', 'pwd', 'get_all',
            'path2str', 'str2path', 'invisible', 'BS', 'cwd', 'color_str',
            'FG_COLORS', 'BG_COLORS', 'sh'
          ]
