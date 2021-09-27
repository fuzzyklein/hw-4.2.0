"""Run the program."""

from pprint import pp
import sys

from driver import Driver
from hw import HelloWorld

if __name__ == '__main__':
    if {'-t', '--testing'}.intersection(sys.argv):
        Driver().run()
    else:
        HelloWorld().run()
