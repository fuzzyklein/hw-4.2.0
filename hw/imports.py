from bs4 import BeautifulSoup
from cmd import Cmd
columnize = Cmd().columnize
import glob
import importlib.resources
from io import StringIO
import os
from os import chdir, curdir, listdir
from pathlib import Path
import pkg_resources
from pprint import pprint as pp
import re
import requests
import site
import sys
import zipfile

from pandas import DataFrame, Series

site.addsitedir(Path.home() / 'Development/hw-4.2.0/hw')
