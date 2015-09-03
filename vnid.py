#!/usr/bin/env python3
import socket
import json
import sys
import os

CREDENTIALS = {
  "protocol": 1,
  "client": "vnid",
  "clientver": "0.2.0",
}

#API_IP = '188.165.210.64'
# use api.vndb.org if this one fails
API_IP = '188.165.233.33'
API_PORT = 19534

class Item:
  def __init__(self, original_arg, type_="", id_=0, title=""):
    self.original_arg = original_arg
    self.type = type_
    self.id = id_
    self.title = title
  def __str__(self):
    return "{\"%s\" \"%s\" %i \"%s\"}" % (self.original_arg, self.type, self.id, self.title)

if len(sys.argv) < 2:
  print("usage: %s [id]..." % os.path.basename(sys.argv[0]))
  exit(2)

s = socket.socket()

jsonify = lambda x: ' '.join(x.split(' ')[1:])

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

def cmd_query_items(s, items, flag="basic"):
  queries = {} # key: exact query command (no filters), value: id list
  results = []

  for i in items:
    if type(i) != Item:
      raise TypeError(str(i) + ": the \'items\' argument of query_items() can only take lists of the Item class instances (got " + type(i) + ")")

    query_cmd = "get " + i.type + " " + flag

    if query_cmd in queries and queries[query_cmd]:
      queries[query_cmd].append(i.id)
    else:
      queries[query_cmd] = [i.id]

  #print(queries)

  for k, v in queries.items():
    #print(json.loads(jsonify(cmd(s, k + " (id = " + json.dumps(v) + ")")))['items'])
    results += json.loads(jsonify(cmd(s, k + " (id = " + json.dumps(v) + ")")))['items']

  for i in items:
    for j in results:
      if i.id == j['id']:
        if j['original']:
          i.title = j['original']
        else:
          i.title = j['title']

  return items


items = [parse_id(x) for x in sys.argv[1:]]
s.connect((API_IP, API_PORT))

cmd(s, "login " + json.dumps(CREDENTIALS))
items = cmd_query_items(s, items)

for i in items:
  print(i.original_arg + '\t' + i.title)

s.close()
