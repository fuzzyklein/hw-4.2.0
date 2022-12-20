from http.server import CGIHTTPRequestHandler, HTTPServer
from os import environ
import socket
import sys
from threading import Thread
import time
import webbrowser

from .globals import BASEDIR
from .program import Program
from .tools import run

class HelloWorld(Program):
    def process_file(self, p):
        super().process_file(p)

    def run(self):
        super().run()
        print('Hello world')
        VERBOSE = self.settings['verbose']
        # Check to see if a Web server is running in the base directory.
        # Check to see if port 8001 is busy.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        LOCATION = ('localhost', 8001)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if ERROR := s.connect_ex(LOCATION):
                if self.settings['verbose']: print("Server port is closed.")
            else:
                if self.settings['verbose']: print("server port is open.")
                print('Closing program')
                sys.exit(ERROR)

        # TODO: Determine how an existing Python web server can be shut down programatically.
        #       Even if that's possible, is it the proper thing to do?

        # print(f'{ERROR=}')
        assert(ERROR)

        def serve_http():
            print("Serving HTTP")
            # run(f'python3.10 -m http.server -d {BASEDIR} --bind localhost'.split())
            HTTPServer(LOCATION, CGIHTTPRequestHandler).serve_forever()


        t = Thread(target=serve_http, daemon=True)
        t.start()

        environ['BROWSER'] = 
        webbrowser.open(f'http://{LOCATION[0]}:{LOCATION[1]}/html/index.html')

        # Listen on port 8002 for a signal to stop the application.

        # s.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 8002))
            s.listen()
            conn, addr = s.accept()
            # with conn:
            #     print('Connected by', addr)
            #     while True:
            #         data = conn.recv(1024)
            #         if not data:
            #             break
            #         conn.sendall(data)

        print('Good night!')
