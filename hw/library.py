from datetime import date
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
        self.cursor = self.cnx.cursor()
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
                        if self.DEBUG:
                            print()
                            print(f'Info for {str(p)}:')
                            pp(info)
                        link = f'{self.OCLC}/classify2/ClassifyDemo?search-standnum-txt={info["ISBN-13"]}&startRec=0'
                        if self.DEBUG:
                            print(f'First Link: {link}')
                        response = requests.get(link)
                        soup = BeautifulSoup(response.text, features='lxml', parser='lxml')
                        ddc = soup.find('tbody').find_all('td')[1].text
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

                        statement = f'SELECT * FROM books WHERE ISBN=\'{info["ISBN-13"]}\';'
                        self.cursor.execute(statement)
                        # result = self.cnx.cmd_query(statement)
                        if not len(list(self.cursor)):
                            for author in info["Authors"]:
                                names = author.split()
                                statement = f"""SELECT * FROM Authors WHERE First='{author[0]}' AND Last='{author[-1]}';"""
                                self.cursor.execute(statement)
                                if not len(list(self.cursor)):
                                    statement = f"""INSERT INTO Authors (First, Last) VALUES('{names[0]}', '{names[-1]}');"""
                                    self.cursor.execute(statement)
                                    if len(names) > 2:
                                        middle = sum(names[1:-1])
                                        statement = f"""INSERT INTO Authors (Middle) VALUES('{middle}');"""
                                pub = info['Publisher']
                                statement = f"""SELECT FROM pubs * WHERE Publisher='{pub}';"""
                                if not len(list(self.cursor)):
                                    statement = f"""INSERT INTO pubs (Publisher) VALUES('{pub}');"""
                                    self.cursor.execute(statement)

                            statement = f"""INSERT INTO books(Title, Category, Filepath, Date, ISBN) VALUES('{info["Title"]}', '{ddc}', '{p.name}', {date(int(info["Year"]),1,1)}, {info["ISBN-13"]});"""
                            self.cursor.execute(statement);
                            self.cnx.commit()
                            statement = f"""SELECT ID FROM books WHERE TITLE='{info['Title']}';"""
                            self.cursor.execute(statement)
                            book_id = self.cursor.fetchone()
                            print(book_id)
                            if self.DEBUG: trace()
                            if not book_id:
                                warn('Failed to get book record!')
                                return
                            else:
                                print(f'Book ID: {book_id}')
                                for i, author in enumerate(info['Authors']):
                                    names = author.split()
                                    print(f'{names=}')
                                    statement = f"""SELECT ID FROM Authors WHERE First='{names[0]}' AND Last='{names[-1]}';"""
                                    self.cursor.execute(statement)
                                    author_id = self.cursor.fetchone()
                                    print(f'{author_id=}')
                                    if not author_id:
                                        warn('Failed to get author record!')
                                        return
                                    else:
                                        statement = f"""INSERT INTO contribs(Book, Author, Priority) VALUES({book_id[0]}, {author_id[0]}, {i})"""
                                        print(statement)
                                        self.cursor.execute(statement)
                                        self.cnx.commit()
                        else:
                            warn(f'Book {info["Title"]} is already in the database.')
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
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

def main():
    Library().run()

if __name__ == '__main__':
    main()
