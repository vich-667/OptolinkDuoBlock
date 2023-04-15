#!/usr/bin/python3
"""
Created on 12.10.2019

@author: vich
"""
import json
import logging
import abc
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


JSON_HEADER = {"Content-type": "application/json; charset=utf-8"}
HTML_HEADER = {"Content-type": "text/html; charset=utf-8"}
TEXT_HEADER = {"Content-type": "text/plain; charset=utf-8"}

log = logging.getLogger("RestAPIServer")


class IController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_status(self, thing=None):
        pass

    @abc.abstractmethod
    def set_value(self, channel, value):
        pass


class _ControllerMock(IController):
    def get_status(self, thing=None):
        things = {
            "itemA": {
                "state": "do",
                "position1": 100,
                "position2": 0
            },
            "itemB": {
                "state": "idle",
                "detection": False
            }
        }

        if thing:
            return {thing: things[thing]}
        else:
            return things

    def set_value(self, channel, value):
        return True


class SetExcept(Exception):
    pass


class RestAPIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            atomic_path = [elem for elem in urlparse(self.path).path.split('/') if elem]

            if not atomic_path:
                atomic_path.append("getstatus")

            if atomic_path[0] == "getstatus":
                log.debug("Get status from all controllers")
                content = self.server.controller.get_status()

            else:
                # we can have also channel = atomic_path[:-1]
                log.debug('Get status from %s' % atomic_path[0])
                content = self.server.controller.get_status(atomic_path[0])

            body = json.dumps(content)
            body = body.encode("utf-8")
            self.__send_response(JSON_HEADER, body)
        except Exception as e:
            log.exception(f"Can't process request! {e}")
            self.send_error(404)

    def do_POST(self):
        try:
            atomic_path = [elem for elem in urlparse(self.path).path.split('/') if elem]
            if not atomic_path[0] == "set":
                raise SetExcept("We only work on /set/*")

            if len(atomic_path) > 1:
                channel = atomic_path[1:]

                msg_len = int(self.headers['Content-length'])
                post_msg = self.rfile.read(msg_len)
                value = post_msg.decode("utf-8")

            else:
                query_components = parse_qs(urlparse(self.path).query)
                channel = []
                for key in ['thing', 'item', 'channel']:
                    try:
                        channel.append(query_components[key][0])
                    except KeyError:
                        pass
                # date = query_components['date'][0]
                value = query_components['value'][0]

            if not len(channel) or not value:
                raise SetExcept("Eiter POST or query the new state!")

            log.debug('New value "%s" for channel %s' % (value, str(channel)))
            ret = self.server.controller.set_value(channel, value)

            body = "OK" if ret else "ERROR"
            body = body.encode("utf-8")
            self.__send_response(TEXT_HEADER, body)
        except Exception as e:
            log.exception(f"Can't process request! {e}")
            self.send_error(404)

    def __send_response(self, headers=None, body=None, retcode=200):
        if not headers:
            headers = {}
        self.send_response(retcode)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def log_message(self, format, *args):
        log.info("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    log_format = '%(asctime)-25s %(name)-25s %(levelname)-10s %(message)s (line %(lineno)d in %(filename)s)'
    logging.basicConfig(format=log_format, level=logging.NOTSET)

    httpd = HTTPServer(('', 8005), RestAPIRequestHandler)
    httpd.controller = _ControllerMock()
    httpd.serve_forever()
