#!/usr/bin/python3

import os
import re
import glob
import json
import zlib
import math
import copy
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

def sortbylen(x):
    if type(x) == list:
        return len(x)
    return 0

def tocpathtoobj(p):
    r = { }
    for pel in p:
        if "name" in pel and "level" in pel:
            r[pel["level"]] = pel["name"]
    return r

# init
sources = { }

# load compiled sources
sources = load_json("compiled/sources.json")

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")
if not os.path.exists("compiled/tables"):
    os.mkdir("compiled/tables")

# get a list of tables to process
tablescan = [ ]
g = glob.glob("tables/**/*--base.json",recursive=True)
for path in g:
    basepath = str(path)
    if not basepath[-11:] == "--base.json":
        raise Exception("What??")
    basepath = basepath[0:len(basepath)-11]
    tablescan.append({ "base path": basepath, "base json path": path })

# process base descriptions
for scan in tablescan:
    path = scan["base json path"]
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    #
    ji = load_json(path)
    if not "id" in ji:
        continue
    if not "base definition" in ji:
        raise Exception("Table "+ji["id"]+" does not indicate base definition, but has --base.json extension")
    if not ji["base definition"] == True:
        raise Exception("Table "+ji["id"]+" is not base definition, but has --base.json extension")
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename == (ji["id"] + "--base.json"):
        raise Exception("Table "+ji["id"]+" id does not match filename "+basename)
    # our JSON has schema version numbers now, because in the future we may have to make
    # some changes
    if not "schema" in ji:
        raise Exception("Table "+ji["id"]+" has no schema information")
    if not "version" in ji["schema"]:
        raise Exception("Table "+ji["id"]+" has no schema version")
    ver = ji["schema"]["version"]
    if ver < 1 or ver > 1:
        raise Exception("Table "+ji["id"]+" is using unsupported schema "+str(ver))
    # table column name to index lookup
    if "table columns" in ji:
        tablecols = ji["table columns"]
        if not type(tablecols) == list:
            raise Exception("Table "+ji["id"]+" columns not an array")
        refby = { }
        for coli in range(0,len(tablecols)):
            col = tablecols[coli]
            if not type(col) == dict:
                raise Exception("Table "+ji["id"]+" column "+str(coli)+" not an object")
            if not "name" in col:
                raise Exception("Table "+ji["id"]+" column "+str(coli)+" has no name")
            colname = col["name"]
            if colname in refby:
                raise Exception("Table "+ji["id"]+" column "+str(coli)+" name "+colname+" already exists")
            refby[colname] = coli
        #
        ji["table name to column"] = refby
    else:
        raise Exception("Table "+ji["id"]+" has no columns defined")
    #
    ji["schema"]["compiled version"] = 1
    ji["source json file"] = path
    #
    #
    write_json("compiled/tables/"+ji["id"]+".json",ji);

