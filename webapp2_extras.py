"""
Stubs to change behaviour of webapp2 functions and classes
"""


class Routes:
    """ Fake Routes module """
    class PathPrefixRoute:
        """ prefix lots of paths """
        def __init__(self, prefix, routes_list):
            self.url = prefix
            self.routes_list = routes_list


routes = Routes()


class Jinja:
    """ Fake Jinja module """
    pass


jinja2 = Jinja()
