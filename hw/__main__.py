from traceback import print_exc
from warnings import warn

from hw.hw import HelloWorld

def main():
    """ main()

        Call the `run` method of a class descended from `py.Program`.
    """
    print("Hello, World!")
    try:
        if False: warn("What the fuck? :D")
    except:
        print_exc()
        exit()
    HelloWorld().run()
    print("Goodbye!")

if __name__ == "__main__":
    main()
