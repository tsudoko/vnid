#!/usr/bin/env python3
import json
import logging
import sys
import time
import os

import vndb_simple

CREDENTIALS = {
    "client": "vnid",
    "clientver": "0.6.1",
}


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
    if len(id_) > 2 and not id_[1:].isdigit():
        raise Exception("invalid id string: %s" % id_)

    if id_.startswith("v"): # "v" <vn-id>
        return Item(id_, "vn", int(id_[1:]))
    elif id_.startswith("r"): # "r" <release-id>
        return Item(id_, "release", int(id_[1:]))
    elif id_.isdigit: # <vn-id>
        return Item(id_, "vn", int(id_))
    else:
        raise Exception("invalid id string: %s" % id_)


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
        wait = 0

        while True:
            if wait:
                time.sleep(wait)
                wait = 0

            try:
                response = s.cmd(k + " (id = " + json.dumps(v) + ") " + json.dumps({"page": i}))
            except vndb_simple.VNDBThrottle as e:
                mw, wait = map(float, e.split(":"))
                logging.warning("throttled, resend after %fs and wait %fs" % (mw, wait))
                time.sleep(mw)
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
    s = vndb_simple.VNDBSession(credentials=CREDENTIALS)

    try:
        items = query_items(s, items)

        for i in items:
            print(i.original_arg + '\t' + i.title)
    finally:
        s.close()

if __name__ == "__main__":
    main()
