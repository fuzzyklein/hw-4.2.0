""" Define a class that parses simple configuration files. """

from configparser import ConfigParser
import logging
from os import environ, sep
from pathlib import Path
from pprint import pprint as pp
from warnings import warn

from ansicolortags import printc

from globals import *
from tools import *

class Configure(dict):
    """ Same thing as a `ConfigParser`, but simpler. """

    CONFIG_FILE = BASEDIR / ('etc' + sep + f'{PROGRAM}.conf')
    if __debug__: print(f'{CONFIG_FILE=}')

    DEFAULT = """[DEFAULT]
# Uncomment this line to send `logging` messages to a file.
logfile = log/ws.log
template = /home/fuzzy/Development/hw-4.2.1
"""

    def __init__(self, file=None):
        """ Parse the file and store the values.

            :file: Configuration file to be parsed.
                   (default is `None`, in which case `DEFAULT` is used.)
        """

        # print(f'{args=}\n{bool(args)=}\n{kwargs=}')
        super().__init__()
        # print("Reading configuration file...")
        try:
            if __debug__:
                print()
                print("DEBUGGING CONFIGURATION CLASS INITIALIZER...")
                print()
                printc(f"<cyan>Configuration file<reset>: {self.CONFIG_FILE}")
                print()
                i = 0
            for line in [s for s in Path(self.CONFIG_FILE).read_text().split('\n')
                         if s and not s.startswith('#')]:
                if __debug__:
                    printc(f"<cyan>Line {i}<reset>: {line}")
                    i += 1
                item = line.split('=')
                self.update({item[0].strip() : item[1].strip()})
        except FileNotFoundError:
            parser.read_string(self.DEFAULT)
        except TypeError:
            warn("Support for Python 3.8 will be phased out in due course.")
            self.update(parser['DEFAULT'])
