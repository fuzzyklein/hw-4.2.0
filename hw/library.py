from getpass import getuser
import json
import os
from pathlib import Path
from pdb import set_trace as trace
from pprint import pprint as pp
from shutil import copy2 as cp
import site
import subprocess
from warnings import warn

from bs4 import BeautifulSoup
import isbnlib
import mysql.connector
# import pdfminer
import requests

BASEDIR = Path.home() / 'Development/hw-4.2.0'
site.addsitedir(str(BASEDIR / 'hw'))

from tools import *
from program import Program

class Library(Program):
    def __init__(self):
        super().__init__()
        self.results = list()
        self.cnx = mysql.connector.connect(user=getuser(),
                                           password=(Path.home()/self.settings['pass_file']).read_text(),
                                           host='192.168.254.71',
                                           database='library')
        self.OCLC = 'http://classify.oclc.org'
        self.DDC_FILE = (BASEDIR / 'data/deweysummaries.txt').read_text().split('\n')
        self.BOOKS_DIR = BASEDIR / 'tests/library/books'

    def process_file(self, p):
        self.info(f'Processing file {str(p)}')
        if p.name.endswith('.pdf'):
            l = list()
            try:
                l = list(map(lambda s: str(s).lstrip('b').strip("'"),
                             [s for s in run(['pdf2txt.py', str(p)]).split('\n') if s.startswith('ISBN')]))
            except subprocess.CalledProcessError:
                warn('pdf2txt.py returned an error code!')
                return
            if l:
                info = dict()
                for n in l:
                    try:
                        info = isbnlib.meta(l[0].split()[-1])
                    except isbnlib.NotValidISBNError as e:
                        warn(f'Invalid ISBN in file {p.name} : {l[0].split()[-1]}')
                        break
                    if info:
                        print()
                        print(f'Info for {str(p)}:')
                        pp(info)
                        link = f'{self.OCLC}/classify2/ClassifyDemo?search-standnum-txt={info["ISBN-13"]}&startRec=0'
                        if self.DEBUG: print(f'First Link: {link}')
                        response = requests.get(link)
                        soup = BeautifulSoup(response.text, features='lxml', parser='lxml')
                        ddc = soup.find('tbody').find_all('td')[1].text
                        # if not link:
                        #     print(f"Could not get a link from OCLC for {str(p)}")
                        #     if self.DEBUG: trace()
                        #     return
                        # link = f"{self.OCLC}{link['href']}"
                        # response = requests.get(link)
                        # soup = BeautifulSoup(response.text)
                        # ddc = soup.find('tbody').find('tr').find_all('td')[1].text
                        numbers = [ddc[0] + '00', ddc[:2] + '0', ddc[:3]]
                        classes = list()
                        for i, n in enumerate(numbers):
                            classes.extend([' '.join(s.split()[1:]) for s in self.DDC_FILE if s.startswith(numbers[i])])
                        classes = [s for s in classes if len(s)]
                        classes = [numbers[i] + ' ' + classes[i] for i in range(3)]
                        classdir = self.BOOKS_DIR / classes[0] / classes [1] / classes[2]
                        if not classdir.exists():
                            os.makedirs(classdir)
                        dest = classdir / p.name
                        if not dest.exists():
                            cp(p, dest, follow_symlinks=self.settings['follow'])
                        else:
                            self.info(f'File {dest} already exists.')

                    else:
                        warn(f'Failed to get info for {p.name}')
            else:
                warn(f'Failed to get ISBN for {p.name}')
        else:
            warn(f'File {str(p)} is not a book')

    def run(self):
        self.process_args()
        self.shutdown()

    def process_args(self):
        if not self.settings['args']: self.settings['args'] = ['*']
        super().process_args()

    def shutdown(self):
        self.cnx.close()


def main():
    Library().run()

if __name__ == '__main__':
    main()
