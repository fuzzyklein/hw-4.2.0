from hw.program import Program
from hw.driver import Driver

class HelloWorld(Program):
    def __init__(self, settings=None):
        super().__init__()

    def run(self):
        print("Running the Hello World! program class' `run` method.")
        super().run()
        Driver(self.settings).cmdloop()
