import lldb
import os
import logging

from functools import wraps

LOGGER = logging.getLogger(__name__)

def require(*attrs):
    def inner(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if any(getattr(self, a, None) is None for a in attrs):
                LOGGER.warn(
                    "(In function %s) "
                    "Not all attributes in %r are defined",
                    fn.__name__, attrs
                )

                return

            return fn(self, *args, **kwargs)

        return wrapper

    return inner


class Controller(object):
    def __init__(self, target, args=()):
        self.path = target
        self.args = list(args) or None
        self.debugger = self.target = self.process = None

    def __enter__(self):
        self.debugger = lldb.SBDebugger.Create()
        self.debugger.SetAsync(False)
        self.target = self.debugger.CreateTargetWithFileAndArch(
            self.path, lldb.LLDB_ARCH_DEFAULT)

        return self

    def __exit__(self, *args):
        state = self.state
        if self.state not in (lldb.eStateExited, lldb.eStateInvalid):
            self.kill()

        if self.target:
            self.debugger.DeleteTarget(self.target)
            self.target = None

        if self.debugger:
            lldb.SBDebugger.Destroy(self.debugger)
            self.debugger = None

    def launch(self):
        self.process = self.target.LaunchSimple(
            self.args, None, os.getcwd())

        return self.process is not None

    @require("process")
    def state(self):
        return self.process.GetState()

    @require("target")
    def set_breakpoint(self, name):
        bp = self.target.BreakpointCreateByName(name)
        return bp.id

    @require("target")
    def delete_breakpoint(self, id_):
        return self.target.BreakpointDelete(id_)

    def command(self, cmd):
        ci = self.debugger.GetCommandInterpreter()
        res = lldb.SBCommandReturnObject()
        ci.HandleCommand(cmd, res)
        return res

    @require("target")
    def evaluate(self, expr):
        value = self.target.EvaluateExpression(
            expr, lldb.SBExpressionOptions())

        return str(value)

    @require("process")
    def frames(self):
        return list(self.process.GetThreadAtIndex(0))

    @require("process")
    def cont(self):
        self.process.Continue()

    @require("process")
    def kill(self):
        self.process.Kill()
        self.process = None
