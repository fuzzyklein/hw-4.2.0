""" Define the `Arguments` class. """

from argparse import ArgumentParser
import inspect
import logging
import sys

from globals import PROGRAM

STD_OPTS = [[[],
  {"dest": "args",
   "metavar": "ARGUMENTS",
   "nargs": "*",
   "help": "Files to be processed."
  }
 ],

      [["-V", "--version"], {"action": "version", "version": "ncv 0.0.0", "help": "Display the program name and version, then exit."}],
      [["-d", "--debug"], {"action": "store_true", "dest": "debug", "help": "Set to run the program in DEBUG mode."}],
      [["-v", "--verbose"], {"action": "store_true", "dest": "verbose", "help": "Display extra information."}],
      [["-r", "--recursive"], {"action": "store_true", "dest": "recursive", "help": "Process files recursively."}],
      [["-t", "--testing"], {"action": "store_true", "dest": "testing", "help": "Run the `doctest`s in `main.py`"}],
      [["-f", "--follow"], {"action": "store_true", "dest": "follow", "help": "Follow symbolic links."}],
      [["-a", "--all"], {"action": "store_true", "dest": "all", "help": "Process hidden files."}],
      [["-c", "--config"], {"dest": "config", "help": "Specify a configuration file."}],
      [["-i", "--input"], {"dest": "input", "help": "Specify a file to be used as input."}],
      [["-o", "--output"], {"dest": "output", "help": "Specify a file to be used as output."}],
      [["-q", "--quiet"], {"action": "store_true", "dest": "quiet", "help": "Suppress screen output."}],
      [["-l", "--log"], {"dest": "log", "help": "Specify a log file."}],
      [["-w", "--warnings"], {"dest": "warnings", "help": "Display warning messages."}]
    ]

class Arguments(dict):
    """ Parse the command line arguments and store the relevant values. """

    import __init__

    INIT_DOCSTR = [line for line in inspect.getdoc(__init__).split('\n') if line]
    DESCRIPTION = INIT_DOCSTR[1]
    EPILOG = INIT_DOCSTR[-1]

    def __init__(self, *args, **kwargs):
        """ Use an `ArgumentParser` object to parse the command line.

            :args: and :kwargs: are passed to the `dict.__init__` function.
        """

        super().__init__(*args, **kwargs)

        parser = ArgumentParser(prog=PROGRAM, description=self.DESCRIPTION, epilog=self.EPILOG)

        for option in STD_OPTS:
            parser.add_argument(*option[0], **option[1])

        self.update(vars(parser.parse_args(sys.argv[1:])))
