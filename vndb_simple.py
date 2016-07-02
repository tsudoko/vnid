import socket
import json


class VNDBError(Exception):
    pass


class VNDBSession:
    __s = None
    # used in __str__()
    __addr = None
    __port = None

    def __init__(self, addr="api.vndb.org", port=19534, credentials={}):
        credentials['protocol'] = 1

        self.__s = socket.socket()

        self.__s.connect((addr, port))
        self._cmd("login " + json.dumps(credentials))

        self.__addr = addr
        self.__port = port


    def __str__(self):
        return "<VNDBSession (%s:%s)>" % (self.__addr, self.__port)


    def _parse_response(self, response):
        r = response.split(' ')

        name = r[0]
        json_ = json.loads(' '.join(r[1:]))

        if name == "error":
            raise VNDBError(json_['id'] + (": " + json_['msg'] if "msg" in json_ and json_['msg'] else ''))

        return json_


    def _cmd(self, msg):
        data = b""
        now = b""

        self.__s.send(bytes(msg + "\x04", "UTF-8"))

        while not now.endswith(b"\x04"):
            now = self.__s.recv(1024)
            if not now:
                break # should protect from infinite loops on a broken connection
            data += now

        return data.decode().strip("\x04")


    def close(self):
        self.__s.close()


    def cmd(self, msg):
        return self._parse_response(self._cmd(msg))
