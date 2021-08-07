from pathlib import Path
import pdb
import site

# pdb.set_trace()
site.addsitedir(str(Path(__file__).parent))

from program import Program
from driver import Driver

class HelloWorld(Program):
    def __init__(self, settings=None):
        super().__init__()

    def run(self):
        if self.settings['verbose']:
            print("Running the Hello World! program class' `run` method.")
        # if self.settings['debug']: assert 'startup' in self.settings.keys()
        super().run()
        if self.settings['debug']: pdb.set_trace()
        print("Hello, World!")
        if self.settings['testing']:
            Driver(self.settings).cmdloop()
        if self.settings['debug']: pdb.set_trace()
