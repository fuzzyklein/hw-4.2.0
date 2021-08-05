from traceback import print_exc
from warnings import warn

from hw.hw import HelloWorld

def main():
    """ main()

        Call the `run` method of a class descended from `py.Program`.
    """
    # print("Hello, World!")
    try:
        HelloWorld().run()
    except:
        print_exc()
        exit(1)

if __name__ == "__main__":
    main()
