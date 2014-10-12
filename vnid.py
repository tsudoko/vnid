#!/usr/bin/env python3
import socket
import json
import sys
import os

CREDENTIALS = {
  "protocol": 1,
  "client": "vnid",
  "clientver": 0,
}

#API_IP = '188.165.210.64'
# use api.vndb.org if this one fails
API_IP = '188.165.233.33'
API_PORT = 19534

if len(sys.argv) < 2:
  print("usage: %s [id]..." % os.path.basename(sys.argv[0]))
  exit(2)

s = socket.socket()

def cmd(s, msg):
  s.send(bytes(msg + "\x04", "UTF-8"))
  return s.recv(512).decode().strip("\x04")


ids = json.dumps([x for x in sys.argv[1:]])
s.connect((API_IP, API_PORT))

cmd(s, "login " + json.dumps(CREDENTIALS))

"""
info = ' '.join(cmd(s, "get vn basic (id = " + ids + ")").split(' ')[1:])
for i in json.loads(info)['items']:
  print(i['title'])
"""

print(cmd(s, "get vn basic (id = " + ids + ")"))

s.close()
