#!/usr/bin/env python3
import json
import sys
import os

import vndb_simple

CREDENTIALS = {
    "client": "vnid",
    "clientver": "0.4.2",
}

API_IP = '188.165.233.33' # api.vndb.org takes a while to resolve for some reason, so we're using the IP address


class Item:
    def __init__(self, original_arg, type_="", id_=0, title=""):
        self.original_arg = original_arg
        self.type = type_
        self.id = id_
        self.title = title

    def __str__(self):
        return "{\"%s\" \"%s\" %i \"%s\"}" % (self.original_arg, self.type, self.id, self.title)


# id ::= "v" <vn-id> | "r" <release-id> | <vn-id>
def parse_id(id_):
    if id_.startswith("v"): # "v" <vn-id>
        return Item(id_, "vn", int(id_[1:]))
    elif id_.startswith("r"): # "r" <release-id>
        return Item(id_, "release", int(id_[1:]))
    else: # <vn-id>
        return Item(id_, "vn", int(id_))


def query_items(s, items):
    queries = {} # key: exact query command (no filters), value: id list
    results = []

    for i in items:
        if type(i) != Item:
            raise TypeError(str(i) + ": the \'items\' argument of query_items() can only take lists of the Item class instances (got " + type(i) + ")")

        query_cmd = "get " + i.type + " basic"

        if query_cmd in queries and queries[query_cmd]:
            queries[query_cmd].append(i.id)
        else:
            queries[query_cmd] = [i.id]

    for k, v in queries.items():
        i = 1

        while True:
            response = s.cmd(k + " (id = " + json.dumps(v) + ") " + json.dumps({"page": i}))
            results += response['items']

            if not response['more']:
                break

            i += 1

    for i in items:
        for j in results:
            if i.id == j['id']:
                if j['original']:
                    i.title = j['original']
                else:
                    i.title = j['title']

    return items


def main():
    if len(sys.argv) < 2:
        print("usage: %s [id]..." % os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(1)

    items = [parse_id(x) for x in sys.argv[1:]]

    try:
        s = vndb_simple.VNDBSession(addr=API_IP, credentials=CREDENTIALS)
        items = query_items(s, items)

        for i in items:
            print(i.original_arg + '\t' + i.title)

    finally:
        s.close()

if __name__ == "__main__":
    main()
