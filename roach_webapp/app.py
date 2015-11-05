import cherrypy
from pkg_resources import resource_filename


STATIC_ROOT = resource_filename(__name__, "static")

config = {
    "/static": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": STATIC_ROOT
    }
}


class App(object):
    def __init__(self):
        pass


def main():
    cherrypy.quickstart(App(), "/", config)


if __name__ == "__main__":
    main()
