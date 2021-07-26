from argparse import ArgumentParser
from collections import ChainMap
from configparser import ConfigParser
import json
import logging
from os import environ
from pathlib import Path
import re
import sys
from traceback import print_exc
import warnings
from warnings import warn

DEBUG = False
VERBOSE = False

if DEBUG:
    VERBOSE = True
    from pprint import pprint as pp

CONFIG_FILE = 'etc/config.ini'
CONFIG = ConfigParser()
CONFIG.read(CONFIG_FILE)
if DEBUG:
    print(f'{CONFIG=}')
assert(CONFIG["DEFAULT"])
assert(CONFIG["ARGUMENTS"])
PROGRAM = CONFIG["DEFAULT"]["program"]

ENVIRONMENT = {k : v for k, v in environ.items() if k[0].islower()}
if DEBUG: print(f'{ENVIRONMENT=}')

parser = ArgumentParser(PROGRAM, Path(CONFIG["ARGUMENTS"]["epilog"]).read_text())
assert(parser)
f = open(CONFIG["ARGUMENTS"]["args_json_file"])
try:
    PARSER_ARGUMENTS = json.load(f)
except json.JSONDecodeError:
    print_exc()
    PARSER_ARGUMENTS = None
    # exit(1)
f.close()

if DEBUG:
    print("Parser Arguments:")
    print()
    pp(PARSER_ARGUMENTS)
    print()

if PARSER_ARGUMENTS != None:
    for arg in PARSER_ARGUMENTS:
        parser.add_argument(*arg[0], **arg[1])
    ARGS = parser.parse_args(sys.argv[1:])
else:
    ARGS = None

if DEBUG:
    print("Arguments:")
    print()
    pp(ARGS)
    print()

CATEGORIES = list()
for s in Path(CONFIG_FILE).read_text().split('\n'):
    m = re.match(r'\[(\w*)\]', s)
    if m:
        CATEGORIES.append(m.group(1))

if DEBUG:
    print("Categories:")
    print()
    pp(CATEGORIES)
    print()

SETTINGS = ChainMap(ENVIRONMENT, *[CONFIG[s] for s in CATEGORIES])
assert(SETTINGS)

if ARGS: SETTINGS = SETTINGS.new_child(vars(ARGS))

if DEBUG:
    print("Command line arguments:")
    print()
    pp(ARGS)
    print()

assert(SETTINGS["logfile"])
LOGFILE = SETTINGS["logfile"]
log_level = logging.WARNING
if SETTINGS["verbose"]:
    VERBOSE = True
    log_level = logging.INFO
if SETTINGS["debug"]:
    DEBUG = True
    log_level = logging.DEBUG

logging.basicConfig(filename=LOGFILE, level=log_level, filemode='w')
log = logging.getLogger("root")
logging.captureWarnings(True)
log.debug(f"loading {__name__} module")

def main():
    """ main()

        Call the `run` method of a class descended from `py.Program`.
    """
    print("Hello, World!")
    if VERBOSE:
        print(f'{__file__=}')
    try:
        warn("What the fuck? :D")
    except:
        print_exc()
        exit()
    print("Goodbye!")

log.debug(f"{__name__} module loaded.")

if __name__ == "__main__":
    main()
