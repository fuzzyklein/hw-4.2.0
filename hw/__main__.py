from traceback import print_exc

from hw.hw import HelloWorld

def main():
    """ main()

        Call the `run` method of a class descended from `py.Program`.
    """
    # print("Hello, World!")
    try:
        # pp(sys.path)
        HelloWorld().run()
    except:
        print_exc()
        exit(1)

if __name__ == "__main__":
    main()
    
    printc("ansicolortags importd")

    # import os
    # print(f'{os.environ["hw_BASEDIR"]=}')
    # print(f'{os.environ["hw_CONFIG_FILE"]=}')
    #
    # from pprint import pprint as pp
    # import sys
    # print("Python Path:")
    # pp(sys.path)
    # print(f'{len(sys.path)=}')
