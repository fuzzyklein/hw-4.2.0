from argparse import ArgumentParser
from collections import ChainMap
from configparser import ConfigParser
import fileinput
from glob import glob
from io import StringIO
import json
import logging
import os
from os import environ
import os.path
from os import chdir as cd, listdir
from pathlib import Path
import pdb
from pprint import pprint as pp
import re
import sys
from traceback import print_exc
import warnings
import xdg.BaseDirectory

class Program():
    """ Define a base class for classes that initialize a self.program_name and define its
        behavior.
    """
    def __init__(self):
        self.debug = False
        self.verbose = False
        self.configure()
        self.program_name = self.config["DEFAULT"]["program"]
        self.getenv()
        self.getargs()
        self.getset()
        self.startlog()

        """ Initialize the object. """
        self.dbgout(" Initializing program...")

        self.settings = dict(self.settings)
        assert(self.settings)
        if self.settings["verbose"]:
            s = StringIO()
            print("Program settings:", file=s)
            print(file=s)
            pp(self.settings, stream=s)
            print(file=s)
            print(s.getvalue())

        # self.get_input()
        if self.settings["verbose"]: print("Program initialized.")

    def dbgout(self, s):
        if self.log:
            self.dbgout(s)
        else:
            print(s)

    def infout(self, s):
        if self.log:
            self.infout(s)
        else:
            print(s)

    def configure(self):
        self.config_file = Path(xdg.BaseDirectory.xdg_config_home) / f"{Path(__file__).parent.name}/config.ini"
        if not self.config_file.exists():
           self.config_file = Path(__file__).parent.parent / "etc/config.ini"
        if self.config_file.exists():
            if self.debug:
                print(f"Configuration file: {self.config_file}")
            assert(self.config_file.exists())
            self.config = ConfigParser()
            assert(self.config)
            self.config.read(self.config_file)

        else:
            print("No configuration file exists.")
            self.config = ConfigParser()
            self.config['DEFAULT'] = { 'program' : str(Path(__file__).parent.name),
                                  'version' : '4.2.0'
                                }
            self.config['ARGUMENTS'] = { 'args_json_file' : str(Path(__file__).parent.parent / 'etc/arguments.json'),
                                         'epilog' : str(Path(__file__).parent.parent / 'data/epilog.txt')
                                       }
            self.config['ENVIRONMENT'] = dict()
            self.config['program'] = { 'logfile' : 'log/program.log' }

        self.categories = list()
        if Path(self.config_file).exists():
            for s in Path(self.config_file).read_text().split('\n'):
                m = re.match(r'\[(\w*)\]', s)
                if m:
                    self.categories.append(m.group(1))
        else:
            self.categories = self.config.keys()

    def getenv(self):
        self.env = {k : v for k, v in environ.items() if k[0].startswith(self.program_name + '_')}

    def getargs(self):
        self.args = None
        if self.config:
            EPILOG_FILE = Path(self.config["ARGUMENTS"]["epilog"]).read_text()
        else:
            EPILOG_FILE = """
If the program is not installed and the current directory is the project
directory:

    ./run [-h] [-V] [-v] [-d] [-r]

If the program is installed:

    program
    python3 -m program

"""
        parser = ArgumentParser(self.program_name, EPILOG_FILE)
        assert(parser)
        if Path(self.config['ARGUMENTS']['args_json_file']).exists():
            f = open(self.config["ARGUMENTS"]["args_json_file"])
            try:
                PARSER_ARGUMENTS = json.load(f)
            except json.JSONDecodeError:
                print_exc()
                PARSER_ARGUMENTS = None
                # exit(1)
            f.close()
        else: PARSER_ARGUMENTS = None

        if PARSER_ARGUMENTS != None:
            for arg in PARSER_ARGUMENTS:
                parser.add_argument(*arg[0], **arg[1])
            self.args = parser.parse_args(sys.argv[1:])
        else:
            self.args = None

    def getset(self):
        if self.config:
            self.settings = ChainMap(self.env, *[self.config[s] for s in self.categories])
        else: self.config = ChainMap(self.env)
        assert(self.settings)
        if self.args: self.settings = self.settings.new_child(vars(self.args))
        if not 'verbose' in self.settings.keys():
            self.settings['verbose'] = False
        if not 'debug' in self.settings.keys():
            self.settings['debug'] = False
        if not 'args' in self.settings.keys():
            self.settings['args'] = list()
        if not 'testing' in self.settings.keys():
            self.settings['testing'] = False
        if not 'logfile' in self.settings.keys():
            self.settings['logfile'] = str(Path(__file__).parent.parent) / f'log/{self.program_name}.log'

    def startlog(self):
        # pdb.set_trace()
        # print(self.settings['logfile'])
        if 'logfile' in self.settings.keys() and Path(self.settings["logfile"]).exists():
            log_level = logging.WARNING
            if self.settings["verbose"]:
                self.verbose = True
                log_level = logging.INFO
            if self.settings["debug"]:
                self.debug = True
                self.verbose = True
                self.settings["verbose"] = True
                log_level = logging.DEBUG

            logging.basicConfig(filename=self.settings["logfile"], level=log_level, filemode='w')
            self.log = logging.getLogger("root")
            logging.captureWarnings(True)
            self.dbgout(f"loading {__name__} module")

            self.log = logging.getLogger(__name__)
        else: self.log = None


    def run(self):
        """ Override this method to provide all the application code if using this class for a command line script. """
        self.infout("Processing arguments...")
        self.process_args()

    def output(self, s):
        """ This method can be overridden, especially for PyGTK+ self.program_names. """
        print(s)

    def get_input(self):
        """ Check for standard input coming in through a pipe. """
        self.infout(" Getting input text...")
        if self.settings["debug"]:
            s = StringIO()
            print("sys.argv:\n", file=s)
            pp(sys.argv[1:], stream=s)
            print(file=s)
            self.dbgout(s.getvalue())
        args = sys.argv[1:]
        for f in sys.argv[1:]:
            p = Path(f)
            if (not p.exists()) or p.is_dir() or (not p.is_file()):
                args.remove(f)
            if p.is_dir() and self.settings["recursive"]:
                for d in os.walk(p):
                    for f2 in d[2]:
                        if not ignore(f2):
                            args.append(os.path.join(d[0], f2))
        self.settings["input text"] = dict()
        with fileinput.input(args) as cin:
            current_file = None
            for line in cin:
                try:
                    new_file = cin.filename()
                    if new_file != current_file:
                        current_file = new_file
                        self.settings["input text"][current_file] = list()
                    self.settings["input text"][current_file].append(line.rstrip('\n'))
                except FileNotFoundError:
                    if self.settings["verbose"]:
                        print(f"file {f.filename()} not found!")

    def process_args(self):
        if self.settings["debug"]:
            s = StringIO()
            print("Arguments detected:", file=s)
            print(file=s)
            pp(self.settings["args"], stream=s)
            self.dbgout(s.getvalue())
        assert("args" in self.settings.keys())
        self.file_list = list()
        if "args" in self.settings.keys():

            for f in self.settings["args"]:
                assert(type(f) is str)
                self.infout(f" Processing {f}...")
                for name in glob(f, recursive=self.settings["recursive"]):

                    self.process_fname(name)

    def process_fname(self, s):
        self.dbgout("Processing a file name...")
        p = Path(s)
        if not p.exists():
            if self.settings["verbose"]:
                print(f"File {s} does not exist.")
                return
            else:
                print("Verbose switch is off!")
        elif p.is_symlink():
            self.process_link(p)
        elif p.is_dir():
            self.process_dir(p)
        elif p.is_file():
            self.process_file(p)

    def process_link(self, p):
        if not self.settings["follow"]:
            if self.settings["verbose"]:
                print(f"File {s} is a symbolic link.")
                return
            else:
                pass
        else:
            process_file(p)

    def process_dir(self, p):
        if not ignore(p):
            if self.settings["verbose"]:
                print(f"Processing directory {str(p)}")
            if self.settings["recursive"]:
                for f in listdir(str(p)):
                    self.process_fname(os.path.join(str(p), f))

    def process_file(self, p):
        self.dbgout(f"self.program_name is processing file {p}")
        if self.settings["verbose"]:
            print(f"Processing file {str(p)}.")
        self.file_list.append(Path(p))

__all__ = ["Program"]

if __name__ == "__main__":
    pass
    # print(f"Testing {__file__}...")
    # try:
    #     import testing
    # except ModuleNotFoundError:
    #     import py.testing


# ## References

# * [self.configParser](https://docs.python.org/3.7/library/self.configparser.html#self.configparser.self.configParser)
# * [ArgumentParser](https://docs.python.org/3.7/library/argparse.html#argparse.ArgumentParser)
