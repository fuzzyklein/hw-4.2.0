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
import sys
from warnings import warn

from ansicolortags import printc
from bs4 import BeautifulSoup
import isbnlib
import mysql.connector
# import pdfminer
import requests

BASEDIR = Path.home() / 'Development/hw-4.2.0'
site.addsitedir(str(BASEDIR / 'hw'))

from tools import *
from program import Program

PDF_VIEWER = 'atril'

class Library(Program):
    def __init__(self, settings=None):
        super().__init__(settings=settings)
        self.program_name = 'library'
        self.results = list()
        self.db_connect()
        self.OCLC = 'http://classify.oclc.org'
        self.DDC_FILE = (self.BASEDIR / 'data/deweysummaries.txt').read_text().split('\n')
        # print(str(self.DDC_FILE))
        self.BOOKS_DIR = self.BASEDIR / 'tests/library/books'
        # sys.exit(0)

    def db_connect(self):
        expected_sql_state = None
        actual_sql_state = None
        output = ''
        try:
            self.cnx = mysql.connector.connect(user=getuser(),
                                               password=(Path.home()/self.settings['pass_file']).read_text(),
                                               host=self.settings['server_ip'],
                                               database=self.program_name)
            self.cursor = self.cnx.cursor()
            if self.settings['verbose']: printc(f'Connected to database <green>{self.program_name}<reset> at <green>{self.settings["server_ip"]}<reset>.')
        except mysql.connector.ProgrammingError as e:
            # print('Caught a ProgrammingError!')
            actual_sql_state = e.sqlstate
            output = '<red>Error:<reset>: '
            if e.errno == 1049:
                output += e.msg
                expected_sql_state = '42000'
            elif e.errno == 1045:
                output += 'wrong password'
                expected_sql_state = '28000'
            elif e.errno == 1698:
                output += 'bad user name'
                expected_sql_state = '28000'
            else:
                printc('<red>Unknown Programming Error!<reset>')
                pp(e)
                print(f'{e.errno=}')
                print(f'{e.sqlstate=}')
                print(f'{e.msg=}')
            printc(output)
            if actual_sql_state != expected_sql_state:
                printc(f'<yellow>Unexpected SQL state<reset>: {actual_sql_state}')
            sys.exit(1)
        except mysql.connector.InterfaceError as e:
            actual_sql_state = e.sqlstate
            output = '<red>Error<reset>: '
            if e.errno == 2003:
                output += e.msg
            else:
                printc('<red>Unknown Interface Error!<reset>')
                pp(e)
                print(f'{e.errno=}')
                print(f'{e.sqlstate=}')
                print(f'{e.msg=}')
            printc(output)
            if actual_sql_state != expected_sql_state:
                printc(f'<yellow>Unexpected SQL state<reset>: {actual_sql_state}')
            sys.exit(1)

    @str2path_method
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
        try:
            return l[0]
        except IndexError:
            return None

    def get_book_info(self, isbn, p):
        try:
            return isbnlib.meta(isbn)
        except isbnlib.NotValidISBNError as e:
            warn(f'Invalid ISBN in file {p.name} : {isbn}')
            return None

    def get_dewey_decimal_classification(self, isbn):
        link = f'{self.OCLC}/classify2/ClassifyDemo?search-standnum-txt={isbn}&startRec=0'
        if self.DEBUG:
            print(f'First Link: {link}')
        response = requests.get(link)
        soup = BS(response.text)
        return soup.find('tbody').find_all('td')[1].text

    def copy_book_2_server(self, p, classdir='Unclassified'):
        ftp = login()
        ftp.cwd('/srv/www/htdocs/library/books')
        if not exists(ftp, classdir):
            ftp.mkd(classdir)
        ftp.cwd(classdir)
        if not exists(ftp, p.name):
            with p.open() as f:
                ftp.storlines(f'PUT {p.name}', f)
        else:
            self.info(f'File {p.name} already exists.')
        ftp.close()

    def db_get_book(self, isbn):
        statement = f'SELECT * FROM books WHERE ISBN=\'{isbn}\';'
        self.cursor.execute(statement)
        # result = self.cnx.cmd_query(statement)
        records = list(self.cursor)
        if records:
            return records[0]
        else:
            return None

    def db_get_author(self, s):
        names = s.split()
        statement = f"""SELECT * FROM Authors WHERE First='{names[0]}' AND Middle='{" ".join(names[1:-1])}' AND Last='{names[-1]}';"""
        self.cursor.execute(statement)
        records = list(self.cursor)
        # TODO: What if more than one author have the same first and last name but different middle sections(names, initials, etc.)?
        if records:
            return records
        else:
            return None

    def db_add_author(self, s):
        names = s.split()
        # TODO: It's gonna be a problem if an author only has one name.
        statement = f"""INSERT INTO Authors (First, Last) VALUES('{names[0]}', '{names[-1]}');"""
        self.cursor.execute(statement)
        if len(names) > 2:
            middle = ' '.join(names[1:-1])
            statement = f"""INSERT INTO Authors (Middle) VALUES('{middle}');"""
            self.cursor.execute(statement)

    def db_get_pub(self, s):
        statement = f"""SELECT FROM pubs * WHERE Publisher='{s}';"""
        self.cursor.execute(statement)
        records = list(self.cursor)
        try:
            return records[0]
        except IndexError:
            return None

    def db_add_pub(self, s):
        statement = f"""INSERT INTO pubs (Publisher) VALUES('{s}');"""
        self.cursor.execute(statement)

    def db_add_book(self, title, ddc, path, year, isbn):
        statement = f"""INSERT INTO books(Title, Category, Filepath, Date, ISBN) VALUES('{title}', '{ddc}', '{path}', {year}, {isbn});"""
        self.cursor.execute(statement);

    def db_get_book_id(self, isbn):
        statement = f"""SELECT ID FROM books WHERE ISBN='{isbn}';"""
        self.cursor.execute(statement)
        try:
            return self.cursor.fetchone()
        except:
            return None

    def db_get_author_id(self, s):
        names = s.split()
        if self.VERBOSE: print(f'{names=}')
        statement = f"""SELECT ID FROM Authors WHERE First='{names[0]}' AND Middle='{" ".join(names[1:-1])}' AND Last='{names[-1]}';"""
        self.cursor.execute(statement)
        try:
            return self.cursor.fetchone()
        except:
            return None

    def db_add_contrib(self, book, author, priority):
        statement = f"""INSERT INTO contribs(Book, Author, Priority) VALUES({book}, {author}, {priority})"""
        if self.VERBOSE: print(statement)
        self.cursor.execute(statement)

    def get_full_classification(self, ddc):
        return [s for s in self.DDC_FILE if s.startswith(ddc)][0]

    @str2path
    def process_file(self, p):
        if self.VERBOSE: self.info(f'Processing file {str(p)}')
        if p.name.endswith('.pdf'):
            isbn = self.get_isbn(p)
            if isbn:
                info = self.get_book_info(isbn, p)
                if info:
                    if self.VERBOSE:
                        print()
                        print(f'Info for {str(p)}:')
                        pp(info)
                    ddc = self.get_dewey_decimal_classification(isbn)
                    if self.VERBOSE:
                        print(f'Dewey Decimal Classification for {info["Title"]}: {ddc}')

                    classdir = self.get_full_classification(ddc)
                    if self.VERBOSE:
                        print(f'Target directory name: {classdir}')
                    self.copy_book_2_server(p, classdir)
                    if not self.db_get_book(isbn):
                        for author in info["Authors"]:
                            if not self.db_get_author(author):
                                self.db_add_author(author)
                            pub = info['Publisher']
                            if not self.db_get_pub(pub):
                                self.db_add_pub(pub)

                        self.db_add_book(info["Title"], ddc, p.name, date(int(info["Year"]),1,1), info["ISBN-13"])
                        self.cnx.commit()
                        book_id = self.db_get_book_id(info['ISBN-13'])
                        if self.VERBOSE: print(f'{book_id=}')
                        # if self.DEBUG: trace()
                        if book_id:
                            # print(f'Book ID: {book_id}')
                            for i, author in enumerate(info['Authors']):
                                author_id = self.db_get_author_id(author)
                                if self.VERBOSE: print(f'{author_id=}')
                                if author_id:
                                    self.db_add_contrib(book_id, author_id, i)
                                    self.cnx.commit()
                                else:
                                    warn(f'Failed to get author record: Author: {author}')
                        else:
                            warn('Failed to get book record!')
                    else:
                        warn(f'Book {info["Title"]} is already in the database.')
                else:
                    warn(f'Failed to get info for {p.name}')
            else:
                warn(f'Failed to get ISBN for {p.name}')
        else:
            warn(f'File {str(p)} is not a book')

    def run(self):
        # self.process_args()

        BOOKS_DIR = Path.home() / 'Library/Python'
        BOOK = 'Doing Math With Python Use Programming To Explore Algebra, Statistics, Calculus, And More!.pdf'
        TEST_FILE = BOOKS_DIR / BOOK
        # print(f'{type(TEST_FILE)=}')
        print(self.get_isbn(TEST_FILE))

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
