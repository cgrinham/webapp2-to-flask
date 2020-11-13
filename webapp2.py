"""
Stubs to change behaviour of webapp2 functions and classes
"""
import importlib
import logging
from flask.views import MethodView
from flask import request, Response
from webapp2_extras import routes


class Route:
    def __init__(self, url, handler, name=None):
        self.url = self.clean_url(url)
        self.handler = handler
        self._name = name

    @property
    def name(self):
        return self._name or self.url.replace("/", '.')

    @staticmethod
    def clean_url(url):
        if not isinstance(url, str):
            return url
        new_url = url.replace(":\d+", "").replace("<", "<int:")
        return new_url


class WSGIApplication:
    def __init__(self, routes_list, debug=False, config=None):
        self.routes_list = self.apply_prefixes(routes_list)
        self.debug = debug
        self.config = config

    def __call__(self, flask_app):
        """ Process list of webapp2 routes and add them to flask app """
        print("-----------------")
        print("-----------------")
        print("Process main.py")
        print("-----------------")
        print("-----------------")
        for route in self.routes_list:
            # Split "handler" path and import the handler class
            if not route.handler:
                print(f"Could not import nonetype handler {route.url}")
                continue

            if not route.url.startswith("/api/v1"):
                # print(f"Skipping currently non-api endpoint")
                continue

            print(route.url)
            if "|" in route.url or "[" in route.url:
                print(f"Skipping currently unsupported url {route.url}")
                continue

            handler_parts = route.handler.split(".")
            route_module_path = ".".join(handler_parts[:-1])
            try:
                route_module = importlib.import_module(route_module_path)
            except ModuleNotFoundError as error:
                logging.exception("An exception occurred")
                print(f"Could not import {route.handler}")
                print(error)
                raise
                continue
            route_func = getattr(route_module, handler_parts[-1])
            flask_app.add_url_rule(
                route.url,
                view_func=route_func.as_view(route.name)
            )
            print(f"Route {route.url} added")

    def apply_prefixes(self, routes_list, prefix=""):
        """
        Process list of routes and apply prefixes to sub routes if route is
        actually an instance of PathPrefixRoute.
        """
        for route in routes_list:
            if isinstance(route, routes.PathPrefixRoute):
                new_prefix = prefix + route.url
                subroutes = self.apply_prefixes(route.routes_list, prefix=new_prefix)
                for x in subroutes:
                    yield x
            else:
                if isinstance(route, tuple):
                    route = Route(*route)
                if prefix:
                    route.url = f"{prefix}{route.url}"
                yield route


def webapp2_request_adapter(flask_request):
    """
    Adapt flask request to match webapp2 request
    """
    def get(key, default=None):
        """ map webapp2 request.get to flask request.args.get """
        return flask_request.args.get(key, default)

    get_function = get

    class GET(object):
        @staticmethod
        def get(*getargs, **getkwargs):
            return get_function(*getargs, **getkwargs)

    flask_request.get = get
    flask_request.GET = GET()
    return flask_request


class RequestHandler(MethodView):
    def dispatch_request(self, *args, **kwargs):
        """
        Add the flask request and response to the handler, monkey patch it to
        match webapp2 request and trigger the webapp2 `dispatch` method.
        """
        self._args = args
        self._kwargs = kwargs
        self.request = webapp2_request_adapter(request)
        self.response = Response()
        return self.dispatch()
        # return self.response

    def dispatch(self):
        return super().dispatch_request(*self._args, **self._kwargs)


def cached_property(func):
    """ Does nothing """
    def wrapper():
        print("Warning! webapp2 cached_property would run here")
        return func()
    return wrapper
