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
books = { }

def tocbyref(refby,contents,hiernames,hlevel,nhierlist):
    if not hlevel in contents:
        return
    hlevelcontent = contents[hlevel]
    for levname in hlevelcontent:
        levent = hlevelcontent[levname]
        srf = copy.deepcopy(hiernames)
        srf[hlevel] = levname
        #
        if not levname in refby:
            refby[levname] = srf
        else:
            raise Exception("Already in TOC, level "+hlevel+" "+levname) # TODO convert to array and append
        #
        if len(nhierlist) > 0:
            tocbyref(refby,levent,srf,nhierlist[0],nhierlist[1:])

def proc_table_of_contents(ji):
    if not "table of contents" in ji:
        return
    toc = ji["table of contents"]
    if not "hierarchy" in toc:
        return
    hierlist = toc["hierarchy"]
    if not type(hierlist) == list:
        raise Exception("TOC hierarchy needs to be array in "+str(ji["id"]))
    # to avoid confusion with other info, names of each part of the hierarchy must start with @
    for hlevel in hierlist:
        if not isinstance(hlevel, str) == True:
            raise Exception("Hierarchy element not a string in "+str(ji["id"]))
        if not hlevel[0:1] == "@":
            raise Exception("Hierarchy names must start with @ to avoid confusion with information in "+str(ji["id"]))
    #
    if not "contents" in toc:
        return
    contents = toc["contents"]
    if not type(contents) == dict:
        raise Exception("TOC contents needs to be object in "+str(ji["id"]))
    #
    # SO: toc = table of contents parent object
    #     hierlist = array of contents from highest to lowest level in hierarchy (TODO: Allow sub-hierarchy if there are weird books like that)
    #     contents = contents object, which we scan here
    #
    # Build an object so that external code can quickly look up contents by some level in the hierarchy
    if "reference by" in toc:
        raise Exception("TOC contents already compiled into lookup in "+str(ji["id"]))
    refby = { }
    #
    if len(hierlist) > 0:
        tocbyref(refby,contents,{ },hierlist[0],hierlist[1:])
    #
    toc["reference by"] = refby

# process
g = glob.glob("sources/**/*.json",recursive=True)
for path in g:
    ji = load_json(path)
    if not "id" in ji:
        continue
    if not "type" in ji:
        continue
    if ji["id"] in books:
        raise Exception("Book "+ji["id"]+" already exists")
    #
    proc_table_of_contents(ji)
    #
    ji["source json file"] = path
    #
    books[ji["id"]] = ji

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

write_json("compiled/sources.json",books);

