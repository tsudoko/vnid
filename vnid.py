#!/usr/bin/env python3
import socket
import json
import sys
import os

CREDENTIALS = {
  "protocol": 1,
  "client": "vnid",
  "clientver": "0.0.2",
}

#API_IP = '188.165.210.64'
# use api.vndb.org if this one fails
API_IP = '188.165.233.33'
API_PORT = 19534

class Item:
  def __init__(self, original_arg, type_="", id_=0):
    self.original_arg = original_arg
    self.type = type_
    self.id = id_
  def __str__(self):
    return "{\"%s\", \"%s\", %i}" % (self.original_arg, self.type, self.id)

if len(sys.argv) < 2:
  print("usage: %s [id]..." % os.path.basename(sys.argv[0]))
  exit(2)

s = socket.socket()

def cmd(s, msg):
  data = ""
  now = b""

  s.send(bytes(msg + "\x04", "UTF-8"))

  while not now.endswith(b"\x04"):
    now = s.recv(1024)
    if not now: break # should protect from infinite loop on a broken connection
    data += now.decode().strip("\x04")

  return data

# id ::= "v" <vn-id> | "r" <release-id> | <vn-id> "_" <release-id> | <vn-id>
def parse_id(id_):
  if id_.startswith("v"): # "v" <vn-id>
    return Item(id_, "vn", int(id_[1:]))
  elif id_.startswith("r"): # "r" <release-id>
    return Item(id_, "release", int(id_[1:]))
  elif '_' in id_: # <vn-id> "_" <release-id>
    split_id = id_.split('_')

    if len(split_id) != 2:
      raise ValueError("invalid id")

    # XXX: (maybe) check if release id matches vn id (would introduce side effects)
    return Item(id_, "release", int(split_id[1]))
  else: # <vn-id>
    return Item(id_, "vn", int(id_))

ids = [parse_id(x).id for x in sys.argv[1:] if parse_id(x).type == "vn"]
ids = json.dumps(ids)
s.connect((API_IP, API_PORT))

cmd(s, "login " + json.dumps(CREDENTIALS))

"""
info = ' '.join(cmd(s, "get vn basic (id = " + ids + ")").split(' ')[1:])
for i in json.loads(info)['items']:
  print(i['title'])
"""

print(cmd(s, "get vn basic (id = " + ids + ")"))

s.close()
