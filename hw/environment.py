""" Define a class to get and store the relevant (lowercase) environment
    variables.
"""

from os import environ

class Environment(dict):
    """ Get any lowercase environment variables and store their values. """

    def __init__(self, d={k:v for k,v in environ.items() if k[0].islower()}):
        """ Just initialize the object using the `d` parameter.

            :d: A `dict` containing the variables to store.
                (default is any lowercase system environment variables)
        """
        
        super().__init__(d)
