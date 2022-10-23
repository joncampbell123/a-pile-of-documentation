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

# init
tables = { }
sources = { }

# load compiled sources
sources = load_json("compiled/sources.json")

# process base descriptions
g = glob.glob("tables/**/*--base.json",recursive=True)
for path in g:
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
    if ji["id"] in tables:
        raise Exception("Table "+ji["id"]+" already exists")
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
    tables[ji["id"]] = ji

# process base descriptions
g = glob.glob("tables/**/*.json",recursive=True)
for path in g:
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    if len(basename) >= 11 and basename[-11:] == "--base.json":
        continue
    #
    ji = load_json(path)
    if not "id" in ji:
        continue
    if "base definition" in ji:
        if ji["base definition"] == True:
            raise Exception("Table "+ji["id"]+" is base definition, but does not have --base.json extension")
    if not ji["id"] in tables:
        raise Exception("Table "+ji["id"]+" does not exist (no base def?)")
    table = tables[ji["id"]]
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename[0:len(ji["id"])+2] == (ji["id"] + "--"):
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
    if not "table columns" in table:
        raise Exception("Table "+ji["id"]+" is missing table columns")
    # source id?
    sourceref = None
    source_id = None
    source_type = None
    if "source" in ji:
        source_obj = ji["source"]
        if "id" in source_obj:
            source_id = source_obj["id"]
        if "type" in source_obj:
            source_type = source_obj["type"]
    # source id must be in file name along with table id. sorry, this is how we maintain sanity.
    if not source_id == None:
        cut = len(ji["id"])+2+len(source_id)
        match = ji["id"] + "--" + source_id
        if len(basename) >= (cut+2) and basename[cut+2:2] == "--":
            match = match + "--"
            cut = cut + 2
        if not basename[0:cut] == match:
            raise Exception("Table "+ji["id"]+" id and source "+source_id+" id does not match filename "+basename)
        # does the source exist?
        if not source_id in sources:
            raise Exception("Table "+ji["id"]+" no such source "+source_id)
        sourceref = sources[source_id]
        if "type" in sourceref and not source_type == None:
            if not sourceref["type"] == source_type:
                raise Exception("Table "+ji["id"]+" source "+source_id+" type mismatch")

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")
if not os.path.exists("compiled/tables"):
    os.mkdir("compiled/tables")

for tablename in tables:
    table = tables[tablename]
    write_json("compiled/tables/"+tablename+".json",table);

