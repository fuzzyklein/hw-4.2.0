from cmd import Cmd
from traceback import print_exc

from program import Program
from tools import run

class Driver(Cmd, Program):
    def __init__(self, *args, settings=None, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        Program.__init__(self, settings=settings)

    def run(self):
        super().run()
        super().cmdloop()

    def do_quit(self, args):
        """Exit the program. """
        yes = {"Yes", "yes", "Y", "y"}
        response = input("Are you sure you want to quit? ")
        if response in yes: return True
        return False

    def do_exit(self, args):
        return self.do_quit(args)

    def do_bye(self, args):
        return self.do_quit(args)

    def do_EOF(self, args):
        print()
        return True

    def preloop(self):
        if self.settings["verbose"]: print ("Initializing driver...")
        return False

    def postloop(self):
        if self.settings["verbose"]: print ("Closing driver ...")
        return True

    def do_eval(self, args):
        """ Evaluate `args` as Python code. """
        try:
            print (eval(args))
        except:
            try:
                print(run(args))
            except:
                print_exc()

    def default(self, args):
        self.do_eval(args)
