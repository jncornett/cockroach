import argparse
import cherrypy
import threading

from roach.controller import Controller
from roach.spinner import IOQueues, Spinner
from roach.server import Helper


THREAD_JOIN_TIMEOUT = 1.0


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parser.add_argument("-t", "--timeout", type=float, default=1.0)
    return parser


def main():
    options = get_parser().parse_args()

    with Controller(options.target, options.args) as controller:

        controller.set_breakpoint("main")
        controller.launch()

        io = IOQueues(options.timeout)

        with Spinner(controller, io, THREAD_JOIN_TIMEOUT) as spinner:
            # FIXME make host/port configurable
            cherrypy.quickstart(Helper(io))



if __name__ == "__main__":
    main()
