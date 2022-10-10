#!/usr/bin/python3

import os
import re
import glob
import json
import zlib
import math
import struct
import pathlib

def load_json(path):
    f = open(path,"r",encoding='utf-8')
    j = json.load(f)
    f.close()
    return j

def write_json(path,ji):
    f = open(path,"w",encoding='utf-8')
    json.dump(ji,f,indent=4)
    f.close()

# init
books = { }

g = glob.glob("sources/*.json",recursive=True)
for path in g:
    ji = load_json(path)
    if not "id" in ji:
        continue
    if not "type" in ji:
        continue
    if ji["id"] in books:
        raise Exception("Book "+ji["id"]+" already exists")
    ji["source json file"] = path
    books[ji["id"]] = ji

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

write_json("compiled/sources.json",books);

