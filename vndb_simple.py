import socket
import json

class VNDBError(Exception):
    pass


def login(addr, port, client_credentials, username="", password=""):
    s = socket.socket()

    login_data = client_credentials

    if bool(username) != bool(password):
        raise Exception("not enough credentials")

    if username and password:
        login_data['username'] = username
        login_data['password'] = password

    s.connect((addr, port))
    cmd(s, "login " + json.dumps(login_data))

    return s


def parse_response(response):
    r = response.split(' ')

    name = r[0]
    json_ = json.loads(' '.join(r[1:]))
    #print(json_)

    if name == "error":
        raise VNDBError(json_['id'] + (": " + json_['msg'] if "msg" in json_ and json_['msg'] else ''))

    return json_


def cmd(s, msg):
    data = b""
    now = b""

    s.send(bytes(msg + "\x04", "UTF-8"))

    while not now.endswith(b"\x04"):
        now = s.recv(1024)
        if not now:
            break # should protect from infinite loop on a broken connection
        data += now

    return data.decode().strip("\x04")


