from os import environ, sep
from pathlib import Path
import site
import sys

BASEDIR = Path(__file__).parent.parent
PROGRAM_NAME = BASEDIR.stem.split('-')[0]
# print(f'{PROGRAM_NAME=}')
environ[f'{PROGRAM_NAME}_BASEDIR'] = str(BASEDIR)
environ[f'{PROGRAM_NAME}_CONFIG_FILE'] = str(BASEDIR / ('etc' + sep + 'config.ini'))

site.addsitedir(str(BASEDIR))
