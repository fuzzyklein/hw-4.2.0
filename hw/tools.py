from cmd import Cmd
from configparser import ConfigParser
from ftplib import FTP
from functools import partial, wraps
from glob import glob
from io import StringIO
from os import chdir as cd
from pathlib import Path
from pprint import pprint as pp
import re
from subprocess import check_output

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

__all__ = [ 'cd', 'pp', 'columnize', 'run', 'public', 'globber', 'configure',
            'get_file_from_server'
          ]
