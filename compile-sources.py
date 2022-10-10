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

def hierarchy_map_gen(hl,ji,sji,el):
    if len(hl) == 0:
        return
    if not "by hierarchy" in ji:
        ji["by hierarchy"] = { }
    level = hl[0]
    n_hl = hl[1:]
    bs = ji["by hierarchy"]
    if not level in bs:
        bs[level] = { }
    bse = bs[level]
    if not level in sji:
        return
    eji = sji[level]
    for ent in eji:
        nel = el.copy()
        nel.append(ent)
        sent = eji[ent]
        bse[ent] = nel
        hierarchy_map_gen(n_hl,ji,sent,nel)

def hierarchy_map(ji):
    if not "hierarchy" in ji:
        return
    hl = ji["hierarchy"]
    if not type(hl) == list:
        return
    hierarchy_map_gen(hl,ji,ji,[])

# process
g = glob.glob("sources/*.json",recursive=True)
for path in g:
    ji = load_json(path)
    if not "id" in ji:
        continue
    if not "type" in ji:
        continue
    if ji["id"] in books:
        raise Exception("Book "+ji["id"]+" already exists")
    #
    ji["source json file"] = path
    #
    hierarchy_map(ji)
    #
    books[ji["id"]] = ji

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

write_json("compiled/sources.json",books);

