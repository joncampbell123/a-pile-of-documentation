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

# scan "contents" in "table of contents" recursively here.
# refby: "reference by" object, to contain keys of content names and objects providing the full hierarchy
# contents: the "contents" object in which to look for string value hlevel. upon recursion this code digs deeper into the object.
# hiernames: object upon which the name of the level and content name are added as recursion runs, becomes the object tied to content names
# hlevel: level name such as "@part", "@section", etc. as recursion is done
# nhierlist: the rest of the list yet to parse. this is the parent call nhierlist with first element removed and given in hlevel
#
# Example:
#
#             "hierarchy": [
# hlevel =      "@part",
# nhierlist ->  "@section",
#               "@subsection" <-
#             ],
#
# contents =  "contents": {
#               "@part": {
#                   "Part 1": {
#                       "title": "Miscellaneous Information",
#                       "@section": {
#                           "Section 1": {
#                               "title": "General Information",
#                               "@subsection": {
#                                   "1.23": {
#                                       "title": "IBM Extended Character Codes",
#                                       "page": "29",
#                                       "source": "IBM PC/XT Technical Reference, page 2-14"
#                                   },
#                                   "1.25": {
#                                       "title": "EBCDIC Character Set",
#                                       "page": "31"
#                                   }
#                               }
#                           }
#                       }
#                   },
#
# Recursion is used to drill deeper into the object
def tocbyref(refby,contents,hiernames,hlevel,nhierlist):
    if "group" in contents:
        group = contents["group"]
        if not type(group) == list:
            raise Exception("Group must be array")
        for groupi in range(0,len(group)):
            ent = group[groupi]
            #
            srf = copy.deepcopy(hiernames)
            #
            if not type(srf["path"]) == list:
                raise Exception("Must be list");
            #
            nfo = { "group index": groupi }
            if "title" in ent:
                nfo["group title"] = ent["title"]
            #
            srf["path"].append(nfo)
            #
            tocbyref(refby,ent,srf,hlevel,nhierlist)
    #
    if not hlevel in contents:
        return
    hlevelcontent = contents[hlevel]
    for levname in hlevelcontent:
        levent = hlevelcontent[levname]
        #
        srf = copy.deepcopy(hiernames)
        #
        if not type(srf["path"]) == list:
            raise Exception("Must be list");
        srf["path"].append({ "level": hlevel, "name": levname });
        #
        if not levname in refby:
            refby[levname] = srf
        else:
            if not type(refby[levname]) == list:
                refby[levname] = [ refby[levname] ] # convert to list
            refby[levname].append(srf)
        #
        if len(nhierlist) > 0:
            tocbyref(refby,levent,srf,nhierlist[0],nhierlist[1:])

# process "table of contents" JSON object
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
    # process contents by hierarchy (TODO: Allow sub-hierarchy if there are weird books like that)
    if len(hierlist) > 0:
        tocbyref(refby,contents,{ "path": [ ] },hierlist[0],hierlist[1:])
    toc["reference by"] = refby

# process
g = glob.glob("sources/**/*.json",recursive=True)
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
    if not "type" in ji:
        continue
    if ji["id"] in books:
        raise Exception("Book "+ji["id"]+" already exists")
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename == (ji["id"] + ".json"):
        raise Exception("Book "+ji["id"]+" id does not match filename "+basename)
    # our JSON has schema version numbers now, because in the future we may have to make
    # some changes
    if not "schema" in ji:
        raise Exception("Book "+ji["id"]+" has no schema information")
    if not "version" in ji["schema"]:
        raise Exception("Book "+ji["id"]+" has no schema version")
    ver = ji["schema"]["version"]
    if ver < 1 or ver > 1:
        raise Exception("Book "+ji["id"]+" is using unsupported schema "+str(ver))
    #
    proc_table_of_contents(ji)
    #
    ji["schema"]["compiled version"] = 1
    ji["source json file"] = path
    #
    books[ji["id"]] = ji

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

write_json("compiled/sources.json",books);

