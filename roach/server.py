# import json
# from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cherrypy

from spinner import Command, Result


class Helper(object):
    def __init__(self, io):
        self.io = io

    def no_data(self):
        return Result(False, "no JSON data received").get_serializable()

    def malformed_data(self, *expected):
        msg = "malformed JSON data, fields {} were missing".format(
            ", ".join(map(repr, expected)))

        return Result(False, msg).get_serializable()

    def timed_out(self):
        return Result(False, "operation timed out").get_serializable()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def command(self):
    # def command(self, raw):
        # try:
        #     data = json.loads(raw)
        # except ValueError:
        #     data = None
        data = getattr(cherrypy.request, "json", None)

        if not data:
            return self.no_data()

        cmd = data.get("command", None)
        if not cmd:
            return self.malformed_data()

        args = data.get("args", ())
        self.io.put_input(Command(cmd, args))

        result = self.io.get_output(wait=True)
        if not result:
            return self.timed_out()

        results = list(self.io.flush_output())
        return [result] + results

"""
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        helper = self.server.helper
        if self.path != "/command":
            self.send_error(500, "use /command")
            return # FIXME send some json back

        if self.headers.get("content-type") != "application/json":
            self.send_error(500, "no JSON")
            return

        length = self.headers.get("content-length")
        try:
            length = int(length)
        except ValueError:
            length = None

        if length is None:
            self.send_error(500, "bad content-length")
            return

        raw = self.rfile.read(length)
        reply = json.dumps(helper.command(raw))

        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", len(reply))
        self.end_headers()
        self.wfile.write(reply)


class Server(HTTPServer):
    def __init__(self, address, io):
        HTTPServer.__init__(self, address, RequestHandler)
        self.helper = Helper(io)
"""
