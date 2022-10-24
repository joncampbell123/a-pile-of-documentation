#!/usr/bin/python3

import os
import re
import csv
import glob
import json
import zlib
import math
import copy
import struct
import pathlib

def load_csv(path):
    ret = { }
    f = open(path,"r",newline='')
    r = csv.reader(f)
    ret["columnnames"] = next(r)
    ret["rows"] = [ ]
    for row in r:
        if len(row) > 0:
            for coli in range(0,len(row)):
                col = row[coli]
                col = re.sub('^ +','',col)
                col = re.sub(' +$','',col)
                row[coli] = col
            ret["rows"].append(row)
    f.close()
    return ret

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

def get_base_tables():
    tablescanret = [ ]
    g = glob.glob("tables/**/*--base.json",recursive=True)
    for path in g:
        basepath = str(path)
        if not basepath[-11:] == "--base.json":
            raise Exception("What??")
        basepath = basepath[0:len(basepath)-11]
        tablescanret.append({ "base path": basepath, "base json path": path })
    #
    return tablescanret

def proccontenttables(scan):
    ret = [ ]
    #
    g = glob.glob(scan["base path"]+"--*.json",recursive=True)
    for path in g:
        if path == scan["base json path"]:
            continue
        ret.append({ "path": path })
    #
    return ret

def procbasetable(scan,obj):
    path = scan["base json path"]
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    #
    if "ji" in obj:
        raise Exception("What??")
    ji = obj["ji"] = load_json(path)
    if not "id" in ji:
        raise Exception("Table in "+path+" does not have an ID")
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
    for what in ["base definition"]:
        if what in ji:
            del ji[what]
    #
    ji["schema"]["compiled version"] = 1
    ji["source json file"] = path
    ji["sources"] = [ ]
    ji["rows"] = [ ]

def xlatebool(column,data):
    if data == None or data == "":
        return False
    if isinstance(data,int):
        return data > 0
    if isinstance(data,float):
        return data > 0.0
    if type(data) == str:
        if data == "1":
            return True
        if data == "0":
            return False
        if data.lower() == "true":
            return True
        if data.lower() == "false":
            return False
        return False
    raise Exception("Not sure how to parse type "+str(type(data))+" val "+str(data))

def xlateuint(column,data):
    if data == None or data == "":
        return 0
    if isinstance(data,int) or isinstance(data,float):
        return data
    if isinstance(data,str):
        if data == "0":
            return 0
        if re.search('^0x[0-9a-fA-F]+ *$',data):
            return int(data,base=16)
        if re.search('^0b[0-1]+ *$',data):
            return int(data,base=2)
        if re.search('^0[0-7]+ *$',data):
            return int(data,base=8)
        if re.search('^[0-9]+ *$',data):
            return int(data,base=10)
        return data
    raise Exception("Not sure how to parse type "+str(type(data))+" val "+str(data))

def tablecolxlate(column,data):
    if data == None or data == "":
        if "default" in column:
            return column["default"]
    if column["type"] == "bool":
        return xlatebool(column,data)
    if column["type"] == "uint8_t" or column["type"] == "uint_t":
        return xlateuint(column,data)
    return data

def tablerowtodatatype(tablecols,drow):
    for coli in range(0,len(tablecols)):
        if coli >= len(drow):
            break
        #
        drow[coli] = tablecolxlate(tablecols[coli],drow[coli])

def procconttenttable(scan,obj):
    if not "path" in scan:
        raise Exception("What?")
    path = scan["path"]
    if not "ji" in obj:
        raise Exception("What?")
    table = obj["ji"]
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    if len(basename) >= 11 and basename[-11:] == "--base.json":
        raise Exception("What??")
    #
    ji = load_json(path)
    if not "id" in ji:
        raise Exception("Table in "+path+" does not have an ID")
    if "base definition" in ji:
        if ji["base definition"] == True:
            raise Exception("Table "+ji["id"]+" is base definition, but does not have --base.json extension")
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
    #
    toc = None
    toc_refby = None
    toc_contents = None
    toc_hierlist = None
    if not sourceref == None:
        if "table of contents" in sourceref:
            toc = sourceref["table of contents"]
            if not type(toc) == dict:
                raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents not object")
            if "hierarchy" in toc:
                toc_hierlist = toc["hierarchy"]
                if not type(toc_hierlist) == list:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents hierarchy not array")
            if "contents" in toc:
                toc_contents = toc["contents"]
                if not type(toc_contents) == dict:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents contents not object")
            if "reference by" in toc:
                toc_refby = toc["reference by"]
                if not type(toc_refby) == dict:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents reference by not object")
    #
    if not source_id == None and not source_obj == None and not sourceref == None:
        if "where" in source_obj:
            where = source_obj["where"]
            if not type(where) == dict:
                raise Exception("Table "+ji["id"]+" source "+source_id+" where not an object")
            lookup = { }
            lookpaths = { }
            for key in where:
                val = where[key]
                if key[0] == '@':
                    lookup[key] = val
            if len(lookup) > 0:
                matches = [ ]
                if toc_contents == None or toc_hierlist == None or toc == None or toc_refby == None:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" where object with no or incomplete table of contents")
                for level in lookup:
                    value = lookup[level]
                    if not value in toc_refby:
                        raise Exception("Table "+ji["id"]+" source "+source_id+" no such "+level+" "+value)
                    robj = toc_refby[value]
                    if type(robj) == dict:
                        robj = [ robj ]
                    for roe in robj:
                        if not "path" in roe:
                            raise Exception("Table "+ji["id"]+" source "+source_id+" no such path for "+level+" "+value)
                        rpath = roe["path"]
                        match = False
                        for pelo in rpath:
                            if "level" in pelo and "name" in pelo:
                                if pelo["level"] in lookup:
                                    if pelo["name"] == lookup[pelo["level"]]:
                                        match = True
                                    else:
                                        match = False
                                        break # from for loop
                        if match == True: # make sure everything the where clause specifies is actually there
                            chk = tocpathtoobj(rpath)
                            for level in lookup:
                                if not level in chk:
                                    match = False
                                    break
                        if match == True: # only add paths where everything matches the where object lookup
                            matches.append(rpath)
                #
                if len(matches) == 0:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" no matches for where clause")
                # the longest path is the authoratative one, match all others against it.
                # to do this, sort longest to shortest.
                # if there is a mismatch and the lookup refers to it, discard the mismatch.
                # if there is a mismatch and the lookup does not refer to it, it's an ambiguity and therefore an error
                if len(matches) > 1:
                    matches.sort(reverse=True,key=sortbylen)
                # first add to where clause
                authoritah = tocpathtoobj(matches[0])
                for level in authoritah:
                    name = authoritah[level]
                    if level in where:
                        if not name == where[level]:
                            print(authoritah)
                            print(where)
                            raise Exception("Whoah, where object mismatch for "+level+"?")
                    else:
                        where[level] = name
                # then go down the array, checking (does nothing if only one match)
                if len(matches) > 1:
                    scan = 1
                    nmatches = [ matches[0] ]
                    while scan < len(matches):
                        pel = tocpathtoobj(matches[scan])
                        match = None
                        for level in lookup:
                            pval = ""
                            if level in pel:
                                pval = pel[level]
                            aval = ""
                            if level in authoritah:
                                aval = authoritah[level]
                            #
                            if pval == aval:
                                match = True
                            else:
                                match = False
                                break
                        #
                        if match == True:
                            print(['match',match])
                            nmatches.append(matches[scan])
                        scan = scan + 1
                    #
                    matches = nmatches
                # if after all the source resolution there are multiple results, then the where clause is ambiguous
                # and more information is needed
                if len(matches) > 1:
                    print(matches)
                    raise Exception("Table "+ji["id"]+" source "+source_id+" where clause is ambigious. More source information needed to select the specific part of the source.")
                #
                where["path"] = matches[0]
    # proc table data
    basetablecols = table["table columns"]
    nametocol = table["table name to column"]
    rows = table["rows"]
    if not "table" in ji and "table in csv" in ji:
        if ji["table in csv"] == True:
            csv_path = path[0:len(path)-5] + ".csv" # replace .json with .csv
            c = load_csv(csv_path)
            ji["table columns"] = c["columnnames"]
            ji["table"] = c["rows"]
    #
    if "table" in ji:
        if "table columns" in ji:
            src_columns = ji["table columns"]
        else:
            src_columns = [ ]
            for ent in basetablecols:
                src_columns.append(ent["name"])
        src_rows = ji["table"]
        if not type(src_columns) == list or not type(src_rows) == list:
            raise Exception("Table "+ji["id"]+" source "+source_id+" table columns or table rows not an array")
        remapfromsrc = [ ] # [src col] -> basetablecols index
        for col in src_columns:
            if col in nametocol:
                remapfromsrc.append(nametocol[col])
            else:
                raise Exception("No such column "+col) # TODO: we could just add the column dynamically in the future...
        for row in src_rows:
            drowobj = { }
            # the code below will append to sources, so the index to list is the length of the list NOW before appending
            if not source_obj == None:
                drowobj["source index"] = len(table["sources"])
            #
            drow = drowobj["data"] = [ "" ] * len(basetablecols)
            for scoli in range(0,len(row)):
                data = row[scoli]
                dcoli = remapfromsrc[scoli]
                drow[dcoli] = data
            #
            tablerowtodatatype(basetablecols,drow)
            #
            rows.append(drowobj)
    #
    ji["source json file"] = path
    for what in ["schema","table in csv","table","table columns","base definition"]:
        if what in ji:
            del ji[what]
    if not source_obj == None:
        ji["source index"] = len(table["sources"])
        table["sources"].append(ji)

def rowsortcolfiltercombine(tcol,col):
    if "combine different" in tcol:
        if tcol["combine different"] == True:
            if tcol["type"] == "string":
                if "case insensitive" in tcol and tcol["case insensitive"] == True:
                    if isinstance(col,str):
                        col = col.lower()
    #
    return col

def rowsortfilter(tcols,row):
    r = [ ]
    for coli in range(0,len(tcols)):
        tcol = tcols[coli]
        col = row[coli] # FIXME: If col is a dict or list, copy!
        #
        if "combine different" in tcol:
            if tcol["combine different"] == True:
                col = "" # for sorting purposes these columns are ignored
        #
        if tcol["type"] == "string":
            if "case insensitive" in tcol and tcol["case insensitive"] == True and isinstance(col,str):
                col = col.lower()
            if "string sort" in tcol:
                if tcol["string sort"] == "numeric" or tcol["string sort"] == "mixed":
                    # it might be something like "180 KB" or "450 foo 3"
                    sp = re.split(' +',col)
                    for spi in range(0,len(sp)):
                        sp[spi] = xlateuint(tcol,sp[spi])
                    col = sp
        if tcol["type"] == "uint8_t" or tcol["type"] == "uint_t":
            col = tablecolxlate(tcol,col)
            if isinstance(col,str) and col == "-": # we allow "-" "N/A" etc
                col = 999999999 # it has to be made into an integer for comparison, Python will not compare str vs int. Make it an int so - often follows values
        #
        r.append(col)
    return r

def tablerowsort(tcols,row):
    r = [ ]
    if "data" in row:
        r = rowsortfilter(tcols,row["data"])
    if "source index" in row:
        si = row["source index"]
        if isinstance(si,int):
            si = [ si ]
        r.append(si)
    return r

def sorttable(obj):
    if not "ji" in obj:
        raise Exception("What?")
    table = obj["ji"]
    if not "rows" in table:
        raise Exception("What?")
    tcols = table["table columns"]
    rows = table["rows"]
    optRev = False
    if "table sort" in table:
        how = table["table sort"]
        if how == "reverse":
            optRev=True
    rows.sort(key=lambda x: tablerowsort(tcols,x),reverse=optRev)

def deduptable(obj):
    # must have been handled with sorttable first!
    if not "ji" in obj:
        raise Exception("What?")
    table = obj["ji"]
    if not "rows" in table:
        raise Exception("What?")
    srows = table["rows"]
    if len(srows) < 1:
        return
    if not "table columns" in table:
        return
    tcols = table["table columns"]
    nrows = [ ]
    sidx = 0
    #
    buildrow = srows[sidx]
    sidx = sidx + 1
    if not "data" in buildrow:
        raise Exception("row with no data")
    if not "source index" in buildrow:
        buildrow["source index"] = [ ]
    if not type(buildrow["source index"]) == list:
        buildrow["source index"] = [ buildrow["source index"] ]
    nrows.append(buildrow)
    while sidx < len(srows):
        duplicate = False
        srow = srows[sidx]
        sidx = sidx + 1
        if not "data" in srow:
            raise Exception("row with no data")
        if not "source index" in srow:
            srow["source index"] = [ ]
        if not type(srow["source index"]) == list:
            srow["source index"] = [ srow["source index"] ]
        srowdat = srow["data"]
        browdat = buildrow["data"]
        srowcmp = rowsortfilter(tcols,srowdat)
        browcmp = rowsortfilter(tcols,browdat)
        #
        if srowcmp == browcmp:
            duplicate = True
        #
        if duplicate == True:
            for coli in range(0,len(tcols)):
                tcol = tcols[coli]
                scol = srowdat[coli]
                bcol = browdat[coli]
                # some columns are "combine different", those are ignored during the compare
                if "combine different" in tcol:
                    if tcol["combine different"] == True:
                        if isinstance(scol,str):
                            if isinstance(bcol,str) and rowsortcolfiltercombine(tcol,scol) == rowsortcolfiltercombine(tcol,bcol):
                                True # ignore
                            elif not scol == "":
                                if type(bcol) == dict:
                                    nobj = bcol
                                else:
                                    o_bcol = bcol
                                    nobj = bcol = browdat[coli] = { }
                                    nobj["type"] = "multiple"
                                    nobj["values"] = [ ]
                                    if not o_bcol == "":
                                        nobj["values"].append({ "source index": buildrow["source index"].copy(), "value": o_bcol })
                                #
                                chidx = 0
                                while chidx < len(nobj["values"]):
                                    if rowsortcolfiltercombine(tcol,scol) == rowsortcolfiltercombine(tcol,nobj["values"][chidx]["value"]):
                                        break
                                    chidx = chidx + 1
                                #
                                if chidx < len(nobj["values"]):
                                    nobj["values"][chidx]["source index"] += srow["source index"]
                                else:
                                    nobj["values"].append({ "source index": srow["source index"].copy(), "value": scol })
            #
            buildrow["source index"] += srow["source index"]
        else:
            buildrow = srow
            nrows.append(buildrow)
        #
    # dedup source index array per row
    for row in nrows:
        if not "source index" in row:
            raise Exception("What?")
        si = row["source index"]
        si.sort()
        p = None
        nsi = [ ]
        for n in si:
            if not p == n: # remove duplicates
                nsi.append(n)
            p = n
        row["source index"] = nsi
    #
    table["rows"] = nrows

# get a list of tables to process
tablescan = get_base_tables()

# process base descriptions
for scan in tablescan:
    obj = { }
    #
    procbasetable(scan,obj)
    contentscan = proccontenttables(scan)
    for content in contentscan:
        procconttenttable(content,obj)
    sorttable(obj)
    deduptable(obj)
    #
    ji = obj["ji"]
    write_json("compiled/tables/"+ji["id"]+".json",ji);

