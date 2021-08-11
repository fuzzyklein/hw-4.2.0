from pathlib import Path
BASEDIR = Path(__file__).parent.parent.absolute()
PROGRAM_NAME = BASEDIR.stem.split('-')[0]

print(f'Base directory: {BASEDIR}')
print(f'Program name: {PROGRAM_NAME}')

from tools import *

# import xdg.BaseDirectory
# public(xdg.BaseDirectory)

from xdg.BaseDirectory import xdg_config_home as CONFIG_DIR, xdg_data_home as DATA_DIR

CONFIG_DIR = Path(CONFIG_DIR) / PROGRAM_NAME
DATA_DIR = Path(DATA_DIR) / PROGRAM_NAME

print(f'Configuration directory: {str(CONFIG_DIR)}')
print(f'Data directory: {str(DATA_DIR)}')

if not CONFIG_DIR.exists(): CONFIG_DIR.mkdir()
if not DATA_DIR.exists(): DATA_DIR.mkdir()

def check_file_exists(f):
    assert(f.exists())
    return f

map(lambda f: check_file_exists(f), [CONFIG_DIR, DATA_DIR])

CONFIG_FILE_NAME = 'config'

CONFIG_FILE = CONFIG_DIR / PROGRAM_NAME / (CONFIG_FILE_NAME + '.ini')
