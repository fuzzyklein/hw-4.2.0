from os import environ, sep
from pathlib import Path
from pdb import set_trace as trace
import site

from program import Program
from tools import *

PDF_VIEWER = 'atril'

class GetISBN(Program):
    def __init__(self):
        super().__init__()

    def get_isbn(self, p):
        l = list()
        try:
            text = pdf2txt(p, lines=True)
            if self.VERBOSE:
                print(f'Text length: {len(text)}')
                print(f'Text: {text}')
            if len(text) > 1:
                l = list(map(lambda s: str(s).lstrip('b').strip("'"),
                             [s for s in text if s.find('ISBN') != -1]))
            else:
                print(f'File {p} could not be converted to text.')
                print("You'll have to find the ISBN yourself. Sorry 'bout that.")
                run([PDF_VIEWER, str(p)])
                l = [input(f"Enter the ISBN number for {p}: ")]
        except subprocess.CalledProcessError:
            warn('pdf2txt.py returned an error code!')
            return None
        return l[0]


    def process_file(self, p):
        if self.VERBOSE: print(f'Processing file {p.name}')
        if p.name.endswith('.pdf'):
            print(self.get_isbn(p))
        else: print(f'{p.name} is not a PDF.')

    def run(self):
        if self.DEBUG: trace()
        super().process_args()

if __name__ == '__main__':
    BASEDIR = Path(__file__).parent.parent
    PROGRAM_NAME = BASEDIR.stem.split('-')[0]
    # print(f'{PROGRAM_NAME=}')
    environ[f'{PROGRAM_NAME}_BASEDIR'] = str(BASEDIR)
    environ[f'{PROGRAM_NAME}_CONFIG_FILE'] = str(BASEDIR / ('etc' + sep + 'config.ini'))

    site.addsitedir(str(BASEDIR))

    pwd()
    GetISBN().run()
