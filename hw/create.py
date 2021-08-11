#!/usr/bin/env python3
from configparser import ConfigParser
from functools import partial
from os import chdir as cd, curdir as pwd, listdir as ls
from pathlib import Path
import re
from shutil import copytree, move
import site

BASEDIR = Path(__file__).parent.parent

site.addsitedir(str(BASEDIR / 'hw'))
from tools import *
from program import Program

class Creator(Program):
    def __init__(self, settings=None):
        super().__init__()

    def run(self):
        super().run()
        if self.settings['verbose']: pp(settings)
        exit()
        CONFIG_FILE = 'etc/config.ini'
        PROJECT_NAME = Path(curdir).absolute().stem
        config = ConfigParser()
        config.read(CONFIG_FILE)
        config['DEFAULT']['program'] = PROJECT_NAME # Path(__file__).parent.parent.stem
        config['PROGRAM']['logfile'] = f'log/{PROJECT_NAME}.log'
        config['PROGRAM']['basedir'] = f'{BASEDIR}'
        with Path(CONFIG_FILE).open(mode='w', encoding='utf-8') as fp:
            config.write(fp)

        RUN_SCRIPT = Path('sh/hw.sh')
        RUN_SCRIPT.write_text(re.sub('hw', PROJECT_NAME, RUN_SCRIPT.read_text()))
        RUN_SCRIPT.rename(f'sh/{PROJECT_NAME}.sh')

        README = Path('README.md')
        README.write_text(re.sub('hw', PROJECT_NAME, README.read_text()))

        PROJECT_CLASS = PROJECT_NAME.capitalize()
        SOURCE = Path('hw/__main__.py')
        SOURCE.write_text(re.sub('hw', PROJECT_NAME, re.sub('HelloWorld', PROJECT_CLASS, SOURCE.read_text())))

        SOURCE = Path('hw/hw.py')
        SOURCE.write_text(re.sub('HelloWorld', PROJECT_CLASS, SOURCE.read_text()))
        SOURCE.rename(f'hw/{PROJECT_NAME}.py')

        SOURCE = Path('index.md')
        SOURCE.write_text(re.sub('hw', PROJECT_NAME, SOURCE.read_text()))

        Path('hw').rename(PROJECT_NAME)

def main():
    Creator().run()

if __name__ == "__main__":
    main()
