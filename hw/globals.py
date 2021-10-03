""" Define some global variables to be accessed from different modules. """

from pathlib import Path

BASEDIR = Path(__file__).parent.parent
PROGRAM = BASEDIR.stem.split('-')[0]
