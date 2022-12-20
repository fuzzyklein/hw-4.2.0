#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()
import sys
import warnings
warnings.simplefilter('ignore')

print("Content-Type: text/html\n")
print("<h1>Hello World</h1>")
sys.exit(0)
