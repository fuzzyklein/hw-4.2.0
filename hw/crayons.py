#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pycli.py
    v0.0.1b

    Provide a simple framework for a command line tool written in Python:

    - Retrieve settings from a JSON configuration file.
    - Check for environment variables with keys that match keys in the settings.
    - Parse the command line arguments, if any, and take appropriate actions.
    - Set up and test the log file at `log/exec.log`.
    - Process positional command line arguments as filenames.
    - Generate its own documentation.
    - Test itself.
    - Install itself, either system-wide or per user.

    To use this shell to write a program that actually does something to the
    files it processes, just define a callback function and pass it to `main`
    or `process_file`. This project is still experimental and untested, but
    that *should* be all you need to do.

    This version was initiated for the benefit of other local projects already
    using the previous one.
"""
# A comment begins with `#` and extends to the end of the line. So a comment
# should really not have any newlines in it. But obviously sometimes the have to
# or they will scroll across 100 pages or more. This really doesn't matter if
# `atom` soft wraps them at 80 characters, and if worse comes to worst maybe
# there should be a script somewhere that will wrap them with hard newlines.

from argparse import ArgumentParser
import atexit
from cmd import Cmd
from doctest import run_docstring_examples, testmod
import fileinput
from importlib import import_module
import inspect
import json
import logging
from logging import getLogger
import os
import os.path
from os.path import basename
from os import getcwd, environ, mkdir
from pathlib import Path
from pdb import set_trace
from pprint import PrettyPrinter
import re
from subprocess import check_output
import sys
from sys import argv
from threading import Thread
from traceback import print_exc
from warnings import simplefilter

from ansicolortags import printc
from greptile import grep_rl
from progress.bar import Bar
import requests
from ZConfig import configureLoggers

simplefilter('default')
pp = PrettyPrinter()

sys.path.insert(0, (str(Path.home() / "Sources")))
from colors import colors

# CHARACTERS
EMPTY = ''
SPACE = ' '
NEWLINE = '\n'
PERIOD = '.'
COLON = ':'
HYPHEN = '-'
SINGLE_QUOTE = "'"
COMMA = ','
ASTERISK = '*'
UNDERSCORE = '_'
# DIRECTORIES
CURRENT_PATH = Path.cwd()

LOGLEVELS = {"NOTSET":   [0],   # A list because I may add other values like functions.
             "DEBUG":    [10],
             "INFO":     [20],
             "WARNING":  [30],
             "ERROR":    [40],
             "CRITICAL": [50]}
LOGLEVEL = LOGLEVELS["WARNING"][0]

# CURRENT_DIR = getcwd()
NOTSET = LOGLEVELS["NOTSET"][0]
DEBUG = LOGLEVELS["DEBUG"][0]
INFO = LOGLEVELS["INFO"][0]
WARNING = LOGLEVELS["WARNING"][0]
ERROR = LOGLEVELS["ERROR"][0]
CRITICAL = LOGLEVELS["CRITICAL"][0]

SCR_COLORS = ["white", "green", "blue", "yellow", "magenta", "red"]
SCR_HEADS = ["", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
SCREEN_LEVEL = LOGLEVELS["WARNING"][0]

USER_BASE = Path.home() / ".local"
""" There are 3 possibilities:

    - The application was installed system-wide by setup.py, in which case the
      directory 2 levels above this file should end with `.egg`
    - The application was installed in ~/.app_name, in which case that directory
      is the base directory.
    - The application is elsewhere in the file system undergoing development. In
      this case whatever directory is 2 levels above this __file__ is fine.

    The last 2 cases don't cause any problems. The first case forces the program
    to use special utilities to access things like the configuration file and
    other resources that won't be where they're expected to be in the file
    system.

    It's kind of a hassle to deal with, so the configuration file and documents
    should be stored in the user path anyway. That solves the whole thing.
"""

class Driver ( Cmd ) :
    """ Implement a command loop. Define a method named "do_<cmd>()" to
        implement any command in the main() loop. Return False to repeat the
        loop.
    """
    intro  = "Enter a command or `Ctrl-D` to exit."
    prompt = "==> "
    NO_SUCH_CMD = "No such command as {}."
    # file   = None # Presumably a script file containing commands and argments
    #               # for functions defined here.
    # SETTINGS = get_settings()
    def __init__(self):
        """ So far, just call the superclass' __init__ function.
        """
        Cmd.__init__(self)

    def do_quit(self):
        """Exit the program. """
        yes = {"Yes", "yes", "Y", "y"}
        response = input("Are you sure you want to quit? ")
        if response in yes: return True
        return False

    def do_EOF(self, args):
        return self.do_quit()

    def do_eval(self, args):
        """ Evaluate `args` as Python code. """
        try:
            print(exec(args))
        except:
            print_exc()

    def do_test(self):
        pass

class PyCLI(object):
    """ Class to run the basic setup for operations of a command line tool.
    """
    def this_files_path(self):
        return Path(__file__).resolve()

    def __init__(self):
        object.__init__(self)
        self.THIS_FILES_PATH = self.this_files_path()
        self.BASE_PATH = self.THIS_FILES_PATH.parent.parent
        self.PROGRAM_NAME = self.THIS_FILES_PATH.parent.stem
        self.VERSION = "v0.0.0c"
        self.INSTALLED_USER = re.match(r'\.',  self.BASE_PATH.stem)
        self.INSTALLED = bool(self.BASE_PATH.suffix == ".egg")
        if self.INSTALLED:
            self.BASE_PATH = Path.home() / (PERIOD + PROGRAM_NAME)
        self.CONFIG_PATH = self.BASE_PATH / "etc/settings.json"
        self.DOCS_DIR = self.BASE_PATH / "htdoc"

        self.PARSER_ARGUMENTS = [[[], {"dest": "args", "metavar": "ARGUMENTS",
           "nargs": "*", "help": "Files to be processed."}],
        [["-V", "--version"], # Pass either string on the command line.
          {"action": "version", # Display the program version and exit.
            "version": ' '.join([self.PROGRAM_NAME, self.VERSION]),
            # Version string to display.
            "help": "Display the program name and version, then exit."
            # Text to be displayed in connection with this option by the ArgumentParser's
            # automatic `--help` facility.
           }],
        [["-D", "--docs", "--documentation"], {"action": "store_true",
          "dest": "docs", "help": "Generate the documentation for this program."
         }],
        [["-d", "--debug"], {"action": "store_true", "dest": "debug",
          "help": "Set to run the program in DEBUG mode."}],
        [["-T", "--test"], {"action": "store_true", "dest": "testing",
          "help": "Run the program's tests."}],
        [["-v", "--verbose"], {"action": "store_true", "dest": "verbose",
          "help": "Display extra information."}],
        [["-o", "--output"], {"action": "store", "dest": "output",
          "metavar": "OUTFILE", "nargs": 1,
          "help": "Specify the output file (or directory)."}],
        [["-r", "--recursive"], { "action": "store_true", "dest": "recursive",
            "help": "Processes all the files within a given directory."}],
        [["-f", "--follow"], { "action": "store_true", "dest": "follow",
            "help": "Follow symlinks."}],
        [["-n", "--hidden"], {"action": "store_true", "dest": "hidden",
          "help": "Process invisible files."}],
        [["-l", "--log", "--logfile"], {"action": "store", "dest": "logfile",
          "metavar": "LOGFILE", "nargs": 1, "help": "Specify a log file."}],
        [["-g", "--loglevel"], {"action": "store",
          "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
          "metavar": "DEBUG | INFO | WARNING | ERROR | CRITICAL",
          "dest": "loglevel", "default": "DEBUG",
          "help": "Set the level of logging to the console.", "nargs": 1}],
        [["-t", "--tempdir"], {"action": "store", "dest": "tempdir",
            "metavar": "TEMPDIR", "nargs": 1,
            "help": "Specify a directory to use for storage of temporary files."
         }],
        [["-c", "--config"], {"action": "store", "dest": "config",
          "default": EMPTY, "metavar": "CONFIGFILE", "nargs": 1,
          "help": "Specify a configuration file to load settings from."}],
        [["-i", "--interact", "--interactive"], {"action": "store_true",
           "dest": "interact",
           "help": "Run an interactive session after the program finishes."}],
        [["-s", "--settings"], {"action": "store_true", "dest": "settings",
          "help": "Edit the configuration file."}]]
        self.settings = dict()
        self.logger = None
        self.config_path = self.CONFIG_PATH

        atexit.register(self.shutdown)

    def helloworld(self):
        self.output("<blue>Screen level<reset>:" + str(SCREEN_LEVEL), INFO)

        self.output("Running {}".format(self.PROGRAM_NAME), INFO)
        # printc("<yellow>Version<reset>: {}".format(sys.version))

    # Load the configuration file
    def config(self):
        self.settings = json.loads(self.config_path.read_text())
        # set_trace()

    def getenv(self):
        # Check for environment variables
        # TODO: Take the intersection of 2 sets here. Just to try it out.
        for k in self.settings.keys():
            if k in environ.keys():
                self.settings[k] = environ[k]

    def getargs(self):
        # Parse any command line arguments
        # TODO: `epilog` should have single newlines replaced with spaces, and then
        #       be wrapped to 80 chars.
        parser = ArgumentParser(self.PROGRAM_NAME, epilog="""This program is a CLI shell. To
        use it just import the `pycli` module and override `main` or `process_file`,
        depending on the requirements of the new program.

        See http://fuzzyklein.github.io/pycli for more details about using `pycli`.
        """)
        global SCREEN_LEVEL
        for arg in self.PARSER_ARGUMENTS:
            parser.add_argument(*arg[0],**arg[1])
        args = parser.parse_args(argv[1:])
        for k, v in vars(args).items():
            if v is not None:
                self.settings[k] = v

        # Check to see if an alternative configuration file was requested.
        # Configuration options will be overridden by more specific options like `-l`.
        if "config" in self.settings.keys() and self.settings["config"]:
            self.settings.update(json.loads(Path(self.settings["config"].read_text())))
        if "debug" in self.settings.keys() and self.settings["debug"]:
            SCREEN_LEVEL = LOGLEVELS["DEBUG"][0]
        elif "verbose" in self.settings.keys() and self.settings["verbose"]:
            SCREEN_LEVEL = LOGLEVELS["INFO"][0]

    # Set up the log file with the `logging` module and `ZConfig`.
    def setuplog(self):
        """ Set up logging.
        """
        if Path("log").exists():
            LOGFILE = self.settings["logfile"]
            # if self.settings["debug"]:
            #     printc("<green>LOGFILE<reset>:", LOGFILE)
            #     printc("<green>loglevel<reset>:", self.settings["loglevel"])
            LOGPATH = Path(LOGFILE)
            LOGDIR = LOGPATH.parent
            if not os.path.exists(str(LOGDIR)):
                LOGDIR.mkdir()
            assert (LOGDIR.exists)
            if not os.path.exists(str(LOGPATH)):
                LOGPATH.touch()
            assert (LOGPATH.exists)
            LOGSETUP = """<logger>
              level {}
              <logfile>
                PATH {}
                format {} %(asctime)s %(levelname)s %(name)s %(message)s
              </logfile>
            </logger>
            """.format(LOGLEVEL, self.settings["logfile"], self.PROGRAM_NAME)

            configureLoggers(LOGSETUP)
            return getLogger()
        else: return None

    def shutdown(self):
        logging.shutdown()
        # if "verbose" in self.settings.keys() and self.settings["verbose"]:
        #     printc(NEWLINE + "<cyan>Logging shut down.<reset>")
        if self.settings["verbose"]:
            print("Goodbye")

    def do_file(self, p): # Preferably a Path object by now.
        # if self.settings["debug"]:
        #     printc("<Cyan><black>Processing file<reset>:", p)
        pass

    def process_file(self, f  # String representation of the path to the file.
                              # Usually obtained through a command line argument.
                    ):
        if not self.settings:
            self.output("`process_file` called without `settings` parameter!", ERROR)
            return
        # if self.settings["verbose"]:
        #     printc("<cyan>process_file(<reset>{}<cyan>)<reset>".format(f))
        p = None
        if type(f) is str:
            p = Path(f)
        elif isinstance(f, Path):
            p = f
        if p is None:
            self.output("Bad parameter type: function process_file({})".format(f)
                   + NEWLINE + "Parameter must be a `Path` or `str` type.", ERROR)
            return
        if not p.exists():
            self.output("File <red>{}<reset> does not exist.".format(p), WARNING)
            return
        # if self.settings["verbose"]:
        #     printc(NEWLINE + "<Blue>Processing file<reset>:", p)
        if p.is_symlink():
            if not self.settings["follow"]:
                self.output("File <cyan>{}<reset> is a symbolic link.".format(p), INFO)
                return
        if p.is_dir() and self.settings["recursive"]:
            self.output(NEWLINE + "<green>Processing files recursively<reset>:", INFO)
            for f2 in file_paths(filtered_walk(f)):
                # if self.settings["verbose"]:
                #     printc(NEWLINE + "<magenta>Calling `callback`<reset>")
                do_file(Path(f2))
        elif p.is_file():
            # if self.settings["verbose"]:
            #     printc(NEWLINE + "<magenta>Calling do_file(p)<reset")
            self.do_file(p)

    def edit_config_file(self):
        thread = Thread(target=lambda: check_output(["xed", CONFIG_PATH]),
                        daemon=True)
        thread.start()
        check_output(["xed", CONFIG_PATH])

    def test(self):
        testmod()
        check_output(BASE_PATH / "tests/testing_docgen.py")

    def docs(self):
        check_output("docgen {}".format(BASE_PATH).split())

    def platform_info(self):
        printc("<yellow>Architecture<reset>:", check_output(["arch"],
               universal_newlines=True).strip())
        printc("<yellow>Platform<reset>: {}".format(sys.platform))
        printc("<yellow>Version<reset>: {}".format(sys.version))
        printc("<yellow>Version Info<reset>: {}".format(sys.version_info))

    def dir_info(self):
        printc("<yellow>Current working directory<reset>:", CURRENT_PATH)
        printc("<yellow>Base directory<reset>:", self.BASE_PATH)
        printc(NEWLINE + "<green>Installed in user directory.<reset>"
                         if self.INSTALLED_USER
                         else "{} is not installed".format(self.PROGRAM_NAME))

    def paths_info(self):
        printc(NEWLINE + "<yellow>System Path<reset>:")
        pp.pprint(environ["PATH"].split(COLON))
        printc(NEWLINE + "<yellow>Python Path<reset>:")
        pp.pprint(sys.path)

    def config_info(self):
        printc(NEWLINE + "<cyan>Configuration file<reset>:", self.CONFIG_PATH)
        printc(NEWLINE + "<cyan>Current settings<reset>:")
        pp.pprint(self.settings)
        printc(NEWLINE + "<cyan>Files to process<reset>:")
        pp.pprint(self.settings["args"])

    def get_input_files(self, check_stdin=False):
        if len(self.settings["args"]) > 0:
            for f in self.settings["args"]:
                assert(type(f) is str)
                self.process_file(f)
        elif check_stdin:
            printc(NEWLINE + "<cyan>Checking `stdin`<reset>. Press `Ctrl-D` to"
                            " exit."
                  )
            sys.argv = sys.argv[0:1]
            input_lines = list()
            with fileinput.input() as pin:
                for line in pin:
                    input_lines.append(line)
                temp_in_path = Path(self.settings["tempdir"]) / "input.txt"
                if not temp_in_path.exists():
                    temp_in_path.touch()
                temp_in_path.write_text(EMPTY.join(input_lines))
                try:
                    assert(type(temp_in_path) is Path)
                except AssertionError:
                    self.output("temp_in_path is not a Path. temp_in_path is a {}".format(type(temp_in_path)), INFO)
                self.process_file(temp_in_path)

    def main(self): # -> int
        """ Run the program, which should set any error code that needs to be
            returned.
        """
        if self.config_path.exists(): self.config()
        self.getenv()
        self.getargs()
        # `debug` and `verbose` options apply to screen output
        if self.settings["debug"]:
            # set_trace()
            SCREEN_LEVEL = LOGLEVELS["DEBUG"][0]
            # self.output("Log file: " + self.settings["logfile"], DEBUG)
        elif self.settings["verbose"]:
            SCREEN_LEVEL = LOGLEVELS["INFO"][0]
        # if self.settings["loglevel"] > SCREEN_LEVEL:
        #     self.settings["loglevel"] = SCREEN_LEVEL
        # if self.settings["debug"]:
        #     print("loglevel:", self.settings["loglevel"])
        self.logger = self.setuplog()
        self.output("Logger initialized.", INFO)
        # TODO: The damn logger is broken again.

        if self.settings["settings"]:
            self.edit_config_file()
            sys.exit(0)

        if self.settings["testing"]:
            self.test()
            sys.exit(0)

        if self.settings["docs"]:
            self.docs()
            sys.exit(0)

        if self.settings["verbose"]:
            self.platform_info()
            self.dir_info()
            self.paths_info()
            self.config_info()

        self.get_input_files()

        ########################################################################
        # Add application code here.
        ########################################################################

        output = """<html>
<head>
    <title>Crayons</title>
    <meta charset="utf-8"/>
    <base href="." />
    <link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
</head>
<body>
<table>
<thead>
<th>Color Name</th><th>Hex Value</th><th>RGB Value</th><th>Sample</th>
</thead>
"""

        for k in colors.keys():
            output += "<tr>" + ("<td>{}</td>"*3).format(k, colors[k].hex_format(), 'RGB({},{},{})'.format(colors[k].red, colors[k].blue, colors[k].green)) \
                    + '<td style="background-color:' + colors[k].hex_format() + '">&nbsp;</td>' \
                    + "</tr>"
        OUTPUT_FILE = Path("out/index.html")
        output += "</body>\n</html>"
        print(output)
        OUTPUT_FILE.write_text(output)
        check_output("firefox {}".format(str(OUTPUT_FILE)).split())
        ########################################################################
        # END application code above this comment.
        ########################################################################
        if self.settings["interact"]:
            Driver(self.settings).cmdloop()

        if self.settings["verbose"]:
            print("Goodbye")

        return 0

    def log(self, log_level, s):
        """ Just call the logging object's `log` function.
        """
        if self.logger:
            self.logger.log(log_level, s)

    def output(self, s, log_level=None):
        """ Log `s` to the logfile and print it to the screen.
        """
        outfile = sys.stdout
        outlevel = log_level if log_level else SCREEN_LEVEL
        if not log_level:
            log_level = LOGLEVEL
        if isinstance(log_level, str):
            log_level = LOGLEVELS[log_level][0]
        if log_level > LOGLEVELS["WARNING"][0]:
            outfile = sys.stderr
        if outlevel >= SCREEN_LEVEL:
            COLOR_INDEX = round(log_level / 10)
            printc('<' + SCR_COLORS[COLOR_INDEX] + '>'
                   + SCR_HEADS[COLOR_INDEX] + '<reset>' + COLON + SPACE + s,
                   file=outfile)
        self.log(log_level, s)

    def take_exception(self, e):
        """ Print the exception and try not to exit, which may or may not work.
        """
        self.output(e, self.CRITICAL)
        print_exc()

if __name__ == "__main__":
    global app
    app = PyCLI()
    app.helloworld()
    sys.exit(app.main())
