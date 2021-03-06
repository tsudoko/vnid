import logging
import socket
import json


class VNDBThrottle(Exception):
    pass


class VNDBError(Exception):
    pass


class VNDBSession:
    __s = None
    # used in __str__()
    __addr = None
    __port = None

    _ = lambda self, x: "%s:%s %s" % (self.__addr, self.__port, x)

    def __init__(self, addr="api.vndb.org", port=19535, use_ssl=True, credentials={}):
        credentials['protocol'] = 1

        self.__s = socket.socket()

        if use_ssl:
            import ssl
            c = ssl.create_default_context()
            self.__s = c.wrap_socket(self.__s, server_hostname=addr)

        self.__s.connect((addr, port))
        self.cmd("login " + json.dumps(credentials))

        self.__addr = addr
        self.__port = port

    def __str__(self):
        return "<VNDBSession (%s:%s)>" % (self.__addr, self.__port)

    def _parse_response(self, response):
        r = response.split(' ')

        name = r[0]
        if len(r) == 1:
            return None

        j = json.loads(' '.join(r[1:]))

        if name == "error":
            if j['id'] == "throttled":
                raise VNDBThrottle("%f:%f" % (j['minwait'], j['fullwait']))

            raise VNDBError(j['id'] + (": " + j['msg'] if "msg" in j and j['msg'] else ''))

        return j

    def _cmd(self, msg):
        data = b""
        now = b""

        logging.debug(self._("<< %s") % msg)
        self.__s.send(bytes(msg + "\x04", "UTF-8"))

        while not now.endswith(b"\x04"):
            now = self.__s.recv(1024)
            if not now:
                break # should protect from infinite loops on a broken connection
            data += now

        response = data.decode().strip("\x04")
        logging.debug(self._(">> %s") % response)
        return response

    def close(self):
        self.__s.close()

    def cmd(self, msg):
        return self._parse_response(self._cmd(msg))
