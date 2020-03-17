#!/usr/bin/env python
from os import path
import requests

DEST_DIR = "dest"

def read(file):
    dest_path = path.join(DEST_DIR, file)

    r = requests.post("http://localhost:8000/crypt/",
                      data=dict(operation="read",
                                filepath=file))
    if r.status_code != 200:
        print(r, r.text)
        return

    #print(r.content)
    with open(dest_path, "bw") as f:
        f.write(r.content)

def write(filepath):
    with open(filepath, "rb") as f:
        r = requests.post("http://localhost:8000/crypt/",
                          data=dict(operation="write",
                                    filepath=path.basename(filepath)),
                          files=dict(file=f))
    print(r)
    print(r.text)


#read("lorem.txt")
write("/home/elmjag/area51/webcrypt/rnd2")
read("rnd2")
