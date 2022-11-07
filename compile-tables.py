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

import apodjson

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

# load on demand
def sources_load(sources,source_id):
    if not source_id in sources:
        sources[source_id] = apodjson.load_json("compiled/sources/"+source_id+".json")
    if source_id in sources:
        return sources[source_id]
    return None

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")
if not os.path.exists("compiled/tables"):
    os.mkdir("compiled/tables")

def xlatebool(column,data):
    if data == None or data == "":
        return False
    if isinstance(data,int):
        return data > 0
    if isinstance(data,float):
        return data > 0.0
    if type(data) == str:
        if data == "1" or data == "x" or data == "X":
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

def xlatefloat(column,data):
    if data == None or data == "":
        return 0
    if isinstance(data,int) or isinstance(data,float):
        return data
    if isinstance(data,str):
        if data == "0":
            return 0
        if re.search('^[0-9]+(\.[0-9]*){0,1} *$',data):
            return float(data)
        return data
    raise Exception("Not sure how to parse type "+str(type(data))+" val "+str(data))

def tablecolxlate(column,data):
    if type(data) == list:
        r = [ ]
        for scol in data:
            r.append(tablecolxlate(column,scol))
        return r
    #
    if data == None or data == "":
        if "default" in column:
            data = column["default"]
    if column["type"] == "bool":
        return xlatebool(column,data)
    if column["type"] == "uint8_t" or column["type"] == "uint_t":
        return xlateuint(column,data)
    if column["type"] == "float":
        return xlatefloat(column,data)
    return data

def chartoregex(x):
    # array separator is supposed to be a single char, re.split() takes regex.
    # if someone specifies multiple chars, well, then, they want a regex.
    if x == "|" or x == "\\" or x == "[" or x == "]" or x == "(" or x == ")" or x == "+" or x == "." or x == "'" or x == "\"":
        return "\\" + x
    return x

def get_base_tables():
    tablescanret = [ ]
    #
    g = glob.glob("tables/**/base.json",recursive=True)
    for path in g:
        pp = pathlib.PurePath(path)
        if len(pp.parts) < 2:
            raise Exception("What?")
        if not pp.parts[-1] == "base.json":
            raise Exception("What?")
        basepath = str(pp.parent)
        idmustmatch = str(pp.parts[-2])
        tablescanret.append({ "base path": basepath, "base json path": path, "id must match": idmustmatch })
    #
    return tablescanret

def get_content_tables(scan):
    ret = [ ]
    #
    g = glob.glob(scan["base path"]+"/*.json",recursive=True)
    for path in g:
        if path == scan["base json path"]:
            continue
        pp = pathlib.PurePath(path)
        if len(pp.parts) < 2:
            raise Exception("What?")
        basepath = str(pp.parent)
        idmustmatch = str(pp.parts[-2])
        ret.append({ "base path": basepath, "path": path, "id must match": idmustmatch, "file name": str(pp.name) })
    #
    return ret

def procbasetable(scan,obj):
    path = scan["base json path"]
    #
    if "ji" in obj:
        raise Exception("What??")
    ji = obj["ji"] = apodjson.load_json(path)
    if not "id" in ji:
        raise Exception("Table in "+path+" does not have an ID")
    if not ji["id"] == scan["id must match"]:
        raise Exception("File name "+path+" parent directory name does not match id")
    if not "base definition" in ji:
        raise Exception("Table "+ji["id"]+" does not indicate base definition, but has base.json name "+path)
    if not ji["base definition"] == True:
        raise Exception("Table "+ji["id"]+" is not base definition, but has base.json name "+path)
    # our JSON has schema version numbers now, because in the future we may have to make some changes
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
    # before putting out the final JSON delete certain values
    for what in ["base definition"]:
        if what in ji:
            del ji[what]
    # add notes to JSON, indicating schema compiled version, source JSON
    ji["schema"]["compiled version"] = 1
    ji["source json file"] = path
    # add sources and rows objects for content tables
    ji["sources"] = [ ]
    ji["rows"] = [ ]

def tablerowtodatatype(tablecols,drow,ji):
    for coli in range(0,len(tablecols)):
        if coli >= len(drow):
            break
        #
        if "is array" in tablecols[coli] and tablecols[coli]["is array"] == True and not type(drow[coli]) == list:
            if isinstance(drow[coli],str) and "table column array separator" in ji and isinstance(ji["table column array separator"],str):
                if drow[coli] == "":
                    drow[coli] = [ ]
                else:
                    drow[coli] = re.split(chartoregex(ji["table column array separator"]),drow[coli])
            else:
                drow[coli] = [ drow[coli] ]
            #
            if "is range" in tablecols[coli] and tablecols[coli]["is range"] == True and type(drow[coli]) == list:
                for doli in range(0,len(drow[coli])):
                    drow[coli][doli] = re.split(chartoregex(ji["table column range separator"]),drow[coli][doli])
                    if len(drow[coli][doli]) > 2:
                        raise Exception("Range with more than 2 values")
        #
        drow[coli] = tablecolxlate(tablecols[coli],drow[coli])

def tablerowrangeproccol(tablecols,drowobj,coli):
    if "data" in drowobj:
        drow = drowobj["data"]
        if "is array" in tablecols[coli] and tablecols[coli]["is array"] == True:
            if "is range" in tablecols[coli] and tablecols[coli]["is range"] == True:
                if "range as row" in tablecols[coli] and tablecols[coli]["range as row"] == True:
                    if type(drow[coli]) == list:
                        r = [ ]
                        for ent in drow[coli]:
                            ndr = drowobj.copy() # Remember, Python assignment is pass by reference!
                            ndr["data"] = drow.copy() # and this code is going to duplicate the row and modify it
                            ndr["data"][coli] = [ ent.copy() ] # funny things happen to the rows if we do not do this
                            # TODO: Recurse into this function given drowobj=ndr and coli=coli+1 so secondary columns can expand too. When the need arises.
                            r.append(ndr)
                        return r
    #
    return [ drowobj ]

def tablerowrangeproc(tablecols,drow):
    r = tablerowrangeproccol(tablecols,drow,0)
    return r

def proc_content_table(scan,obj):
    if not "path" in scan:
        raise Exception("What?")
    path = scan["path"]
    if not "ji" in obj:
        raise Exception("What?")
    table = obj["ji"]
    #
    ji = apodjson.load_json(path)
    if not "id" in ji:
        raise Exception("Table in "+path+" does not have an ID")
    if not ji["id"] == scan["id must match"]:
        raise Exception("File name "+path+" parent directory name does not match id")
    if "base definition" in ji:
        if ji["base definition"] == True:
            raise Exception("Table "+ji["id"]+" is base definition, but does not have --base.json extension")
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
    # does the source exist?
    if not source_id == None:
        # the file name must start with the source ID--this is a way to maintain sanity
        fn = scan["file name"]
        if not fn[0:len(source_id)+1] == (source_id+".") and not fn[0:len(source_id)+2] == (source_id+"--"):
            raise Exception("File name "+path+" refers to source "+source_id+" and must start with source ID")
        #
        sourceref = sources_load(sources,source_id)
        if sourceref == None:
            raise Exception("Table "+ji["id"]+" no such source "+source_id)
        if "type" in sourceref and not source_type == None:
            if not sourceref["type"] == source_type:
                raise Exception("Table "+ji["id"]+" source "+source_id+" type mismatch")
    # scan and match source ref to table of contents of source: look up the key JSON objects we need
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
    # scan and match source ref to table of contents of source: take the source ref info and match against table of contents and gen lookup tables
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
    src_cols_present = [ False ] * len(basetablecols)
    rows = table["rows"]
    # some tables store their rows and columns in .csv files
    if not "table" in ji and "table in csv" in ji:
        if ji["table in csv"] == True:
            csv_path = path[0:len(path)-5] + ".csv" # replace .json with .csv
            c = load_csv(csv_path)
            ji["table columns"] = c["columnnames"]
            if not "table column array separator" in ji:
                ji["table column array separator"] = " " # default separate by spaces
            if not "table column range separator" in ji:
                ji["table column range separator"] = "-" # default A-B range
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
                src_cols_present[nametocol[col]] = True
                remapfromsrc.append(nametocol[col])
            else:
                raise Exception("No such column "+col) # TODO: we could just add the column dynamically in the future...
        ji["source columns present"] = src_cols_present.copy()
        for row in src_rows:
            drowobj = { "columns present": src_cols_present.copy() }
            # the code below will append to sources, so the index to list is the length of the list NOW before appending
            if not source_obj == None:
                drowobj["source index"] = len(table["sources"])
            #
            drow = drowobj["data"] = [ "" ] * len(basetablecols)
            #
            if len(row) > len(remapfromsrc):
                print(row)
                raise Exception("Row has too many columns")
            #
            for scoli in range(0,len(row)):
                data = row[scoli]
                dcoli = remapfromsrc[scoli]
                drow[dcoli] = data
            #
            tablerowtodatatype(basetablecols,drow,ji)
            drowar = tablerowrangeproc(basetablecols,drowobj)
            #
            rows += drowar
    #
    ji["source json file"] = path
    for what in ["schema","table in csv","table","table columns","base definition","table column array separator","table column range separator"]:
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

def bytes_from_base_suffix(base_n,unit_n):
    unit_n = unit_n.lower()
    #
    if unit_n == "b" or unit_n == "":
        True # nothing
    elif unit_n == "kb":
        base_n <<= 10
    elif unit_n == "mb":
        base_n <<= 20
    elif unit_n == "gb":
        base_n <<= 30
    elif unit_n == "tb":
        base_n <<= 40
    elif unit_n == "pb":
        base_n <<= 50
    else:
        raise Exception("Unknown suffix "+base_n)
    return base_n

def strtol_bytes(col):
    # "160 KB" "40MB" etc
    res = re.findall('^([0-9]+) *([KMGTP]{0,1}B{0,1})$',col)
    col = 0
    if not res == None and len(res) == 1: # should be either 0 or 1 results
        res = res[0]
        col = bytes_from_base_suffix(int(res[0]),res[1])
    #
    return col

def rowcolsortfilter(tcol,col):
    if type(col) == list:
        r = [ ]
        for scol in col:
            r.append(rowcolsortfilter(tcol,scol))
        return r
    #
    if "combine different" in tcol:
        if tcol["combine different"] == True:
            col = "" # for sorting purposes these columns are ignored
    if tcol["type"] == "string":
        if "case insensitive" in tcol and tcol["case insensitive"] == True and isinstance(col,str):
            col = col.lower()
        if "string sort" in tcol:
            if tcol["string sort"] == "bytes":
                col = strtol_bytes(col)
            if tcol["string sort"] == "numeric" or tcol["string sort"] == "mixed":
                # it might be something like "180 KB" or "450 foo 3"
                sp = re.split(' +',col)
                for spi in range(0,len(sp)):
                    sp[spi] = xlateuint(tcol,sp[spi])
                col = sp
    if tcol["type"] == "float":
        col = tablecolxlate(tcol,col)
        if isinstance(col,str): # we allow "-" "N/A" etc
            col = 99e99 # it has to be made into a float for comparison, Python will not compare str vs int. Make it an int so - often follows values
    if tcol["type"] == "uint8_t" or tcol["type"] == "uint_t":
        col = tablecolxlate(tcol,col)
        if isinstance(col,str): # we allow "-" "N/A" etc
            col = 999999999 # it has to be made into an integer for comparison, Python will not compare str vs int. Make it an int so - often follows values
    return col

def rowsortfilter(tcols,row):
    r = [ ]
    for coli in range(0,len(tcols)):
        r.append(rowcolsortfilter(tcols[coli],row[coli]))
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
    # must have been assembled from all tables first
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
        # ignore any column not provided by both tables in order to allow tables to add to separate
        # columns without causing multiple entries
        for coli in range(0,len(tcols)):
            tcl = tcols[coli]
            # presence merge, if present and set to False, disables merge combining columns across tables.
            # in that case, the column if not provided by the table is treated as the default value being present.
            if "presence merge" in tcl and tcl["presence merge"] == False:
                srow["columns present"][coli] = buildrow["columns present"][coli] = True
            #
            spr = srow["columns present"][coli]
            bpr = buildrow["columns present"][coli]
            if not (spr == True and bpr == True):
                srowcmp[coli] = browcmp[coli] = None
        #
        if srowcmp == browcmp:
            duplicate = True
        #
        if duplicate == True:
            for coli in range(0,len(tcols)):
                if srow["columns present"][coli] == True:
                    if not buildrow["columns present"][coli] == True:
                        buildrow["columns present"][coli] = True
                        browdat[coli] = srowdat[coli]
                        continue
                #
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
        # also clear temp stuff
        del row["columns present"]
        # multiple values may have dupes too
        if "data" in row:
            data = row["data"]
            for dcol in data:
                if type(dcol) == dict:
                    if "type" in dcol and dcol["type"] == "multiple" and "values" in dcol and type(dcol["values"]) == list:
                        for dvo in dcol["values"]:
                            if "source index" in dvo:
                                dsi = dvo["source index"]
                                dsi.sort()
                                p = None
                                ndsi = [ ]
                                for n in dsi:
                                    if not p == n:
                                        ndsi.append(n)
                                    p = n
                                dvo["source index"] = ndsi
                                # if the result is the same as the row source index, then remove it entirely, there is no point
                                if dvo["source index"] == row["source index"]:
                                    del dvo["source index"]
    #
    table["rows"] = nrows

# get a list of tables to process
tablescan = get_base_tables()

# process base descriptions
for scan in tablescan:
    obj = { }
    #
    procbasetable(scan,obj)
    for content in get_content_tables(scan):
        proc_content_table(content,obj)
    sorttable(obj)
    deduptable(obj)
    #
    ji = obj["ji"]
    apodjson.write_json("compiled/tables/"+ji["id"]+".json",ji);

