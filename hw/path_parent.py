#! /usr/bin/env python

# from argparse import ArgumentParser
from pathlib import Path
import sys

# parser = ArgumentParser(description="print the parent directory of a given directory",
#                         epilog="Source code should be self-explanatory.")
# parser.add_argument(**{"dest": "args",
#  "metavar": "ARGUMENTS",
#  "nargs": "*",
#  "help": "Files to be processed."
# })
# parser.parse_args(sys.argv[1:])

print(str(Path(sys.argv[1]).parent.absolute()))
