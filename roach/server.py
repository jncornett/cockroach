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
