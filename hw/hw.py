from hw.program import Program
from hw.driver import Driver

class HelloWorld(Program):
    def __init__(self, settings=None):
        super().__init__()

    def run(self):
        if self.settings['verbose']:
            print("Running the Hello World! program class' `run` method.")
        # if self.settings['debug']: assert 'startup' in self.settings.keys()
        super().run()
        print("Hello, World!")
        if self.settings['testing']: Driver(self.settings).cmdloop()
