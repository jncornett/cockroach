import lldb


class ControllerAdapter(object):
    def __init__(self, controller):
        self.controller = controller

    @classmethod
    def _adapt_arguments(cls, args):
        for arg in args:
            yield cls._adapt_argument(arg)

    @staticmethod
    def _adapt_argument(arg):
        if isinstance(arg, unicode):
            rv = arg.encode("utf-8")
            assert not isinstance(rv, unicode)
            return rv

        return arg

    @staticmethod
    def _adapt_frame_rv(rv):
        pass

    @staticmethod
    def _adapt_cmd_ret_obj_rv(rv):
        return {
            "success": rv.Succeeded(),
            "output": rv.GetOutput(),
            "error": rv.GetError()
        }

    @classmethod
    def _adapt_list_rv(cls, rv):
        for item in rv:
            yield cls._adapt_rv(item)

    @classmethod
    def _adapt_rv(cls, rv):
        if isinstance(rv, (list, tuple)):
            return list(cls._adapt_list_rv(rv))
        elif isinstance(rv, lldb.SBFrame):
            return cls._adapt_frame_rv(rv)
        elif isinstance(rv, lldb.SBValue):
            return str(rv)
        elif isinstance(rv, lldb.SBCommandReturnObject):
            return cls._adapt_cmd_ret_obj_rv(rv)

        return rv

    def send(self, name, *args):
        method = getattr(self.controller, name)
        args = list(self._adapt_arguments(args))
        rv = self._adapt_rv(method(*args))
        return rv
