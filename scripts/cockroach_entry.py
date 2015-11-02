"""
Entry point for the debugger
"""

try:
    import lldb
except ImportError:
    raise # this script only makes sense in the context of the debugger

import abc
import json
import threading
import BaseHTTPServer


DEFAULTS = {
    "address": ("", 8000)
}

STOP_HOOK_COMMAND = "target stop-hook add -o \"script {module}.{hook_name}()"
ERROR_400 = """
<html>
<head>
    <title>{title}</title>
</head>
<body>
<h1>Error {code}</h1>
<p>{message}</p>
</body>
</html>
"""

class Handler(object):
    @abc.abstractmethod
    def handle(self, data):
        pass


class HTTPServerHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """HTTP request handler"""

    handlers = {}

    def get_error(self, code, message, *args, **kwargs):
        return ERROR_400.format(
            title="Oops!",
            code=code,
            message=message.format(*args, **kwargs)
        )

    def send_error(self, code, message, *args, **kwargs):
        self.send_response(code)
        self.wfile.write(self.get_error(code, message, *args, **kwargs))

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_GET(self):
        # to find the handler, we simply replace all . with path sep
        name = self.path.replace("/", ".").strip(".")
        try:
            handler = self.handlers[name]
        except KeyError:
            return self.send_error(
                400, "Handler {!r} does not exist", self.path)

        try:
            # FIXIT Handler and Handler.handle() will probably take some params
            result = json.dumps(handler().handle())
        except Exception as error:
            return self.send_error(400, str(error))

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(result)

    def do_POST(self):
        print "POST"
        print self.headers
        print dir(self.rfile)
        name = self.path.replace("/", ".").strip(".")
        try:
            handler = self.handlers[name]
        except KeyError:
            return self.send_error(
                400, "Handler {!r} does not exist", self.path)

        try:
            raw = self.rfile.read()
            data = json.loads(raw)
        except ValueError as error:
            return self.send_error(400, "JsonDecodeError {!s}: {!r}", error, raw)

        try:
            result = json.dumps(handler().handle(data))
        except Exception as error:
            return self.send_error(400, str(error))

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(result)

    @classmethod
    def register_handler(cls, name, handler):
        cls.handlers[name] = handler


class HTTPServerThread(threading.Thread):

    """HTTP server thread"""

    def __init__(self, **config):
        threading.Thread.__init__(self)
        self.daemon = True
        self.config = config
        self._httpd = None

    def run(self):
        self._httpd = BaseHTTPServer.HTTPServer(
            self.config["address"],
            HTTPServerHandler
        )

        # FIXIT: Add some way to stop this thing
        self._httpd.serve_forever()


# FIXIT: This class should handle a base server object
# FIXIT: This should go in the cockroach module
class Server(object):

    """Manage the HTTP server which is in a separate thread"""

    instance = None

    def __init__(self, **config):
        self.config = dict(DEFAULTS, **config)
        self.thread = HTTPServerThread(**self.config)
        self.thread.start()

    @classmethod
    def get_server(cls, **config):
        if not cls.instance:
            cls.instance = cls(**config)

        return cls.instance


# Handlers
class FooHandler(Handler):
    def handle(self):
        return {"foo": "bar"}


class CommandHandler(Handler):
    def handle(self, data):
        print "handle command", data
        return {"success": True}


def stop_hook():
    print "stop hook hit"


def initialize():

    """initialize the module"""

    lldb.debugger.HandleCommand(STOP_HOOK_COMMAND.format(
        module=__name__,
        hook_name=stop_hook.__name__
    ))

    # register handlers here:
    # HTTPServerHandler.register_handler("foo", foo_handler)
    HTTPServerHandler.register_handler("foo", FooHandler)
    HTTPServerHandler.register_handler("cmd", CommandHandler)

    # start serving
    server = Server.get_server()
