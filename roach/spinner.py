import threading
import Queue
import sys
import traceback

from .adapter import ControllerAdapter


class IOQueues(object):
    def __init__(self, timeout = None):
        self.i = Queue.Queue()
        self.o = Queue.Queue()
        self.timeout = timeout

    def get_input(self, wait=False):
        try:
            return self.i.get(block=wait, timeout=self.timeout)
        except Queue.Empty:
            pass

    def put_input(self, x, wait=False):
        self.i.put(x, block=wait, timeout=self.timeout)

    def get_output(self, wait=False):
        try:
            return self.o.get(block=wait, timeout=self.timeout)
        except Queue.Empty:
            pass

    def put_output(self, x, wait=False):
        self.o.put(x, block=wait, timeout=self.timeout)

    def flush_input(self):
        while not self.i.empty():
            yield self.get_input()

    def flush_output(self):
        while not self.o.empty():
            yield self.get_output()

    def load_input(self, it):
        for item in it:
            self.put_input(item)

    def load_output(self, it):
        for itme in it:
            self.put_output(item)


class Command(object):
    def __init__(self, method, args):
        self.method = method
        self.args = args


class Result(object):
    def __init__(self, success, output, **data):
        self.success = success
        self.output = output
        self.data = data

    def get_serializable(self):
        return {
            "success": bool(self.success),
            "output": self.output,
            "data": self.data
        }


class Spinner(threading.Thread):
    def __init__(self, controller, io, timeout):
        threading.Thread.__init__(self)
        self.adapter = ControllerAdapter(controller)
        self.stop_event = threading.Event()
        self.io = io
        self.daemon = True
        self.timeout = timeout

    def __enter__(self):
        self.start()

    def __exit__(self, *args):
        self.stop()
        if self.is_alive():
            self.join(self.timeout)
            # Oh, well. We tried

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            command = self.io.get_input(wait=True)
            if not command:
                continue

            try:
                rv = self.adapter.send(command.method, *command.args)
            except Exception as e:
                t, value, tb = sys.exc_info()
                # FIXME include backtrace or do some logging
                result = Result(
                    False, str(e),
                    error=str(value),
                    traceback=traceback.extract_tb(tb)
                )
            else:
                # FIXME differentiate on errors
                if isinstance(rv, dict):
                    output = rv.pop("output", "")
                    success = rv.pop("success", False)
                    result = Result(success, output, **rv)

                else:
                    result = Result(True, rv)

            self.io.put_output(result.get_serializable())
