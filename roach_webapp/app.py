import cherrypy
from pkg_resources import resource_filename

STATIC_ROOT = resource_filename(__name__, "static")
print STATIC_ROOT

config = {
    "/": {
        "tools.staticdir.root": ""
    },

    "/static": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": ""
    }
}


class App(object):
    def __init__(self):
        pass

    @cherrypy.expose
    def index(self):
        pass


def main():
    cherrypy.config.update(config)
    cherrypy.quickstart(App())


if __name__ == "__main__":
    main()
