from hw.program import Program

class HelloWorld(Program):
    def __init__(self, settings=None):
        super().__init__()

    def run(self):
        print("Running the Hello World! program class' `run` method.")
        super().run()
