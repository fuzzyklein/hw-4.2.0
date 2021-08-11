from functools import partial
from os import chdir as cd, curdir as pwd, listdir as ls
from pathlib import Path
from pprint import pprint as pp
import sys
from subprocess import check_output

BASEDIR = Path(__file__).parent.parent

sys.path.insert(0, str(BASEDIR / BASEDIR.stem.split('-')[0]))
