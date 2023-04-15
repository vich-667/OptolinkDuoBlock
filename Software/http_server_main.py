#!/usr/bin/python3
"""
Created on 17.10.2019

@author: vich
"""
from http.server import HTTPServer
import logging
import signal
import sys
from threading import Thread
import time

import things
from rest_api_request_handler import IController, RestAPIRequestHandler


# use localhost to listen only locally or '' for everyone
SERVER_ADDRESS = ('localhost', 8006)
# SERVER_ADDRESS = ('', 8006)

log = logging.getLogger("Home Ctrl Extension")


class Controller(IController):
    def __init__(self):
        self.things = {}

    def add_thing(self, thing_name, thing):
        self.things[thing_name] = thing

    def get_status(self, thing_name=None):
        if thing_name:
            return {thing_name: self.things[thing_name].get_status()}
        else:
            status = {}
            for k, v in self.things.items():
                status[k] = v.get_status()
            return status

    def set_value(self, channel, value):
        return self.things[channel[0]].set_value(channel[1:], value)

    def start(self):
        for thing_name in self.things:
            self.things[thing_name].start()

    def shutdown(self):
        for thing_name in self.things:
            self.things[thing_name].shutdown()


def main(debug=""):
    print('Starting up ...')

    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    if debug and debug not in ["log_debug", "log_info", "log_warning"]:
        logging.basicConfig(format=log_format, level=logging.DEBUG)
    elif debug == "log_debug":
        logging.basicConfig(format=log_format, level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    elif debug == "log_info":
        logging.basicConfig(format=log_format, level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    elif debug == "log_warning":
        logging.basicConfig(format=log_format, level=logging.WARNING, handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('log.txt')])
    else:
        logging.basicConfig(format=log_format, level=logging.WARNING)

    # Factor the Things and the Controller
    my_controller = Controller()
    my_controller.add_thing("vito", things.Vito())
    my_controller.start()

    # Start the Server
    http_server = HTTPServer(SERVER_ADDRESS, RestAPIRequestHandler)
    http_server.controller = my_controller
    http_server_thread = Thread(target=http_server.serve_forever)
    http_server_thread.start()

    print('Startup complete')

    if not debug:
        # Ignore failing import on Windows, we are in debug mode
        import systemd.daemon   # type: ignore

        def graceful_exit(signal_number, stack_frame):      # noqa
            systemd.daemon.notify('STOPPING=1')     # type: ignore
            print(f"OptolinkDuoBlock received signal {signal.Signals(signal_number).name}. Stopping now.")
            global run_service
            run_service = False

        print('Register and notify with systemd.')
        # Tell systemd that our service is ready
        systemd.daemon.notify('READY=1')    # type: ignore
        # register SIGTERM and SIGINT handlers to enable graceful shutdown of service
        signal.signal(signal.SIGINT, graceful_exit)
        signal.signal(signal.SIGTERM, graceful_exit)
        print('Running,...')
        global run_service
        while run_service:
            time.sleep(10)
        print('Exiting,...')

    else:
        while True:
            print("Enter command!")
            cmd = input()
            if cmd in ["final", "exit", "stop"]:
                break

    http_server.shutdown()
    http_server_thread.join()
    my_controller.shutdown()


if __name__ == "__main__":
    run_service = True  # global var for systemd
    main("")
