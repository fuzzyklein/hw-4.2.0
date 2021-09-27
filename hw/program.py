"""Define a class that works as a generic file processor."""

from glob import glob
import logging
import os
from os import environ, listdir, makedirs
from pathlib import Path
from pprint import pprint as pp
import sys

from ansicolortags import printc

from arguments import Arguments
from configure import Configure
from environment import Environment
from globals import *
from tools import invisible, str2path_method

class Program():
    """ Abstract class that processes command line arguments as files. """

    def __init__(self, settings=None):
        """ Initialize the application.

            :settings: `dict` containing configuration variables, environment
                       variables, and command line arguments.
        """

        args = Arguments()
        conf = Configure(args['config'])
        env = Environment()

        try:
            self.settings = conf | env | args
        except TypeError:
            printc("<yellow>WARNING<reset>: Python 3.8 support is deprecated.")
            from collections import ChainMap
            self.settings = dict(ChainMap(args, env, conf))

        if __debug__:
            printc('<yellow>Program settings<reset>:')
            pp(self.settings)
            print()

        self.log = self.startlog()
        self.log.debug(f"Debugging {type(self)}")

    def startlog(self):
        """ Set up logging. """
        if __debug__:
            printc('<green>Running<reset> `startlog` ...')
            print(f'{self.settings["logfile"]=}')
        self.logger = logging.getLogger('root')
        if self.settings['log'] or 'logfile' in self.settings.keys():
            p = BASEDIR / (self.settings['log'] if self.settings['log'] else self.settings['logfile'])
            # print(f'{__debug__=}')
            if __debug__:
                printc(f'<cyan>Log file<reset>: {str(p)}')
                print()

            if not p.exists():
                if not p.parent.exists():
                    makedirs(p.parent)
                p.touch()
        else:
            p = None

        if __debug__:
            level = logging.DEBUG
        elif self.settings['verbose']:
            level = logging.INFO
        elif self.settings['warnings']:
            level = logging.WARNING
        else:
            level = logging.ERROR

        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if p:
            fh = logging.FileHandler(p.resolve(), mode='w')
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        logging.captureWarnings(True)
        return logging.getLogger(str(type(self)))

    def run(self):
        """ Process any command line arguments as file names. """

        for f in filter(lambda s: self.settings["all"] or not invisible(s), self.settings["args"]):
            for name in glob(f, recursive=self.settings["recursive"]):
                self.process_fname(name)

    @str2path_method
    def process_fname(self, p):
        """ Dispatch `p` to the appropriate handler.

            :p: `str` or `Path` of the file to be processed.
        """

        # self.log.debug(f"Processing {p.name}...")
        if not p.exists():
            self.log.info(f"File {p.name} does not exist.")
            return
        elif p.is_symlink():
            self.process_link(p)
        elif p.is_dir():
            self.process_dir(p)
        elif p.is_file():
            self.process_file(p)

    def process_link(self, p):
        """ Process the target of the link if `follow` is `True`.

            :p: `str` or `Path` of the file to be processed.
        """

        if self.settings["follow"]:
            process_file(p)
        else:
            self.log.info(f"File {p} is a symbolic link.")

    def process_dir(self, p):
        """ Process the files in the directory if `recursive` is `True`.

            :p: `str` or `Path` of the directory to be processed.
        """

        self.log.info(f"Processing directory {str(p)}")
        if self.settings["recursive"]:
            for f in listdir(p):
                self.process_fname(p / f)

    def process_file(self, p):
        """ Process the file whose `Path` is `p`.

            :p: `str` or `Path` of the file to be processed.
        """

        self.log.info(f"Processing file {p}")
        print(p)
