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
    g = list(glob.glob(scan["base path"]+"/*.json",recursive=True))
    g.sort(key=lambda x: x.lower())
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
            print(tablecols)
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
            if "list source refs" in col:
                ji["source refs on column"] = coli
            # we tell through the output how to interpret things
            col["compiled format"] = "normal" # "" True False int
            if "is array" in col and col["is array"] == True:
                col["compiled format"] = "array" # [ 2 4 6 8 10 ] = 2 4 6 8 10
                if "is range" in col and col["is range"] == True:
                    col["compiled format"] = "array/range" # [ [ 4 ] [ 5 ] [ 7 8 ] [ 9 ] [ 12 14 ] ] = 4 5 7-8 9 12-14
            if "with formatting" in col and col["with formatting"] == True:
                if not col["type"] == "string" or not col["compiled format"] == "normal":
                    raise Exception(path+" column "+colname+" only strings can be used with formatting")
                col["compiled format:array/formatting"] = col["compiled format"]
                col["compiled format"] = "array/formatting" # [ { "type": "text", content: "text content" }, { "type": "linebreak" }, { "type": "text", "bold": true, "content": "bold text" }, ... ]
            if "combine different" in col and col["combine different"] == True:
                col["compiled format:array/combined"] = col["compiled format"]
                col["compiled format"] = "array/combined" # [ { "source index": 4, "value": [ [ 4 ] [ 5 ] [ 7 8 ] [ 9 ] ] } ] where format within array/combined == "array/range"
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

class strscan:
    strval = None
    strpos = None
    def __init__(self,strval):
        self.strval = strval
        self.strpos = 0
    def reset(self):
        self.strpos = 0
    def peek(self,l=1):
        if self.strpos < len(self.strval):
            return self.strval[self.strpos:self.strpos+l]
        return None
    def next(self,l=1):
        self.strpos = self.strpos + l
        if self.strpos > len(self.strval):
            self.strpos = len(self.strval)
    def get(self,l=1):
        c = self.peek(l)
        self.next(l)
        return c
    def eof(self):
        return self.strpos >= len(self.strval)

def formattedsplitnv(text):
    r = { }
    for rent in re.split(r'(?<!\\),',text): # split by , but not \, so commas are possible
        rent = re.sub(r'\\,',',',rent)
        name = rent
        value = ""
        try:
            i = name.index('=')
            value = name[i+1:]
            name = name[0:i]
            if name == "":
                continue
            if name in r:
                r[name] = [ r[name] ]
                r[name].append(value)
            else:
                r[name] = value
        except ValueError:
            print("Warning: splitnv name='"+name+"' with no value which may be a comma that needs escaping")
            True
    return r

def formattedweblink(obj,tcol,splitnv,ji,compiled_format,drowobj):
    if not "url" in splitnv:
        raise Exception("weblink requires URL")
    if not "text" in splitnv:
        splitnv["text"] = splitnv["url"]
    obj["info"] = splitnv

def formattedlink(obj,tcol,splitnv,ji,compiled_format,drowobj):
    if not "type" in splitnv:
        raise Exception("link type missing")
    if not "text" in splitnv:
        splitnv["text"] = splitnv["id"]
    obj["info"] = splitnv

def formattedbitfield(obj,tcol,splitnv,ji,compiled_format,drowobj):
    obj["fields"] = splitnv
    bitmax = -1
    bitmin = 0
    bits = [ ] # index = bit number for checking
    bitr = [ ] # bit index -> entry index
    obj["bitfields"] = [ ]
    for key in splitnv:
        x = re.match(r'bit\[(\d+(:\d+){0,1})]',key)
        if not x == None:
            bittxt = x.group(1) # 4 1 4 or 6:5 4:2 7:0 etc
            try:
                i = bittxt.index(':')
                bmin = bittxt[i+1:]
                bmax = bittxt[0:i]
                bmin = int(bmin)
                bmax = int(bmax)
                if bmin > bmax:
                    bmin,bmax = bmax,bmin # Pythonic swap syntax
            except ValueError:
                bmin = bmax = int(bittxt)
            #
            bitobj = { "min": bmin, "max": bmax, "value": stringtoformatted(tcol,splitnv[key],ji,compiled_format,drowobj) }
            bfi = len(obj["bitfields"])
            if bitmax < bmax:
                bitmax = bmax
            while len(bitr) <= bmax:
                bitr.append(False)
            while len(bits) <= bmax:
                bits.append(None)
            for bit in range(bmin,bmax+1):
                if not bits[bit] == None:
                    raise Exception("Overlapping bit field")
                bits[bit] = True
                bitr[bit] = bfi
            obj["bitfields"].append(bitobj)
    #
    obj["bitdisplay"] = [ ]
    obj["display order"] = "msbfirst"
    for bit in range(bitmin,bitmax+1):
        obj["bitdisplay"].append(bitr[bit])
    #
    obj["bitrange"] = { "min": bitmin, "max": bitmax, "bits": (bitmax+1-bitmin) }

def stringtoformattedtokcurly(tcol,sit,ji,drowobj):
    # "{" was already read
    obj = { }
    txt = ""
    depth = 1
    while True:
        c = sit.get()
        if c == None:
            break
        elif c == "\\":
            txt += c
            c = sit.get()
        elif c == "{":
            depth = depth + 1
        elif c == "}":
            depth = depth - 1
            if depth <= 0:
                break
        #
        if not c == None:
            txt += c
    # txt = tag:data
    # or
    # txt = tag
    tag = txt
    text = None
    try:
        x = tag.index(":")
        text = tag[x+1:]
        tag = tag[0:x]
    except ValueError:
        True
    #
    obj["type"] = tag
    if not text == None:
        if tag == "weblink":
            formattedweblink(obj,tcol,formattedsplitnv(text),ji,tcol["compiled format:array/formatting"],drowobj)
        elif tag == "link":
            formattedlink(obj,tcol,formattedsplitnv(text),ji,tcol["compiled format:array/formatting"],drowobj)
        elif tag == "bitfield":
            formattedbitfield(obj,tcol,formattedsplitnv(text),ji,tcol["compiled format:array/formatting"],drowobj)
        else:
            obj["sub"] = stringtoformatted(tcol,text,ji,tcol["compiled format:array/formatting"],drowobj)
    #
    return obj

def stringtoformattedtok(tcol,sit,ji,drowobj):
    if sit.eof():
        return None
    obj = { }
    #
    if sit.peek() == "\\":
        sit.next()
        c = sit.get()
        if c == "n":
            obj["text"] = "\n"
            obj["type"] = "text"
        elif c == "\\" or c == "{" or c == "}":
            obj["text"] = c
            obj["type"] = "text"
        else:
            raise Exception("Unknown \\escape "+c+" followed by '"+sit.peek(64)+"'")
    elif sit.peek() == "{":
        sit.next()
        obj = stringtoformattedtokcurly(tcol,sit,ji,drowobj)
    else:
        obj["text"] = ""
        obj["type"] = "text"
        while True:
            c = sit.peek()
            if c == None or c == "\\" or c == "{":
                break
            obj["text"] += c
            sit.next()
    #
    return obj

def stringtoformatted(tcol,dcol,ji,compiled_format,drowobj):
    if not compiled_format == "normal":
        raise Exception("With formatting only for strings")
    #
    r = [ ]
    sit = strscan(dcol)
    while True:
        obj = stringtoformattedtok(tcol,sit,ji,drowobj)
        if obj == None:
            break
        #
        if obj["type"] == "text" and len(r) > 0 and r[-1]["type"] == "text":
            r[-1]["text"] += obj["text"]
        else:
            r.append(obj)
    #
    return r

def tablerowtodatatypecol(tcol,dcol,ji,compiled_format,drowobj):
    if compiled_format == "array/combined":
        r = { "source index": [ ji["source index"] ], "value": tablerowtodatatypecol(tcol,dcol,ji,tcol["compiled format:array/combined"],drowobj), "special": { } }
        if "special" in drowobj:
            r["special"] = drowobj["special"]
        if "entry tags" in drowobj:
            r["entry tags"] = drowobj["entry tags"].copy()
        return [ r ]
    if compiled_format == "array/formatting":
        return stringtoformatted(tcol,dcol,ji,tcol["compiled format:array/formatting"],drowobj)
    #
    if compiled_format == "array" or compiled_format == "array/range":
        if "is array" in tcol and tcol["is array"] == True:
            if not type(dcol) == list:
                if isinstance(dcol,str) and "table column array separator" in ji and isinstance(ji["table column array separator"],str):
                    if dcol == "":
                        dcol = [ ]
                    else:
                        dcol = re.split(chartoregex(ji["table column array separator"]),dcol)
                else:
                    dcol = [ dcol ]
            if "is range" in tcol and tcol["is range"] == True and type(dcol) == list:
                for doli in range(0,len(dcol)):
                    dcol[doli] = re.split(chartoregex(ji["table column range separator"]),dcol[doli])
                    if len(dcol[doli]) > 2:
                        raise Exception("Range with more than 2 values")
            return tablecolxlate(tcol,dcol)
    #
    if compiled_format == "normal":
            return tablecolxlate(tcol,dcol)
    #
    raise Exception("table col unknown compiled format "+compiled_format)

def tablerowtodatatype(tablecols,drow,ji,drowobj):
    for coli in range(0,len(tablecols)):
        if coli < len(drow):
            drow[coli] = tablerowtodatatypecol(tablecols[coli],drow[coli],ji,tablecols[coli]["compiled format"],drowobj)

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
    source_index = len(table["sources"]);
    ji["source index"] = source_index
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
            ji["table columns"] = [ ]
            for col in c["columnnames"]:
                if col[0:2] == "__": # special columns
                    continue
                ji["table columns"].append(col)
            if not "table column array separator" in ji:
                ji["table column array separator"] = " " # default separate by spaces
            if not "table column range separator" in ji:
                ji["table column range separator"] = "-" # default A-B range
            ji["table"] = [ ]
            ji["table special"] = [ ]
            for row in c["rows"]:
                nr = [ ]
                ns = { }
                for coli in range(0,len(c["columnnames"])):
                    col = c["columnnames"][coli]
                    if coli < len(row):
                        if col[0:2] == "__": # special columns contain information
                            ns[col[2:]] = row[coli]
                        else:
                            nr.append(row[coli])
                ji["table"].append(nr)
                if len(ns) == 0:
                    ns = False
                ji["table special"].append(ns)
    #
    if "table" in ji:
        if "table columns" in ji:
            src_columns = ji["table columns"]
        else:
            src_columns = [ ]
            for ent in basetablecols:
                src_columns.append(ent["name"])
        if "table special" in ji:
            src_special = ji["table special"]
        else:
            src_special = ji["table special"] = [ ]
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
        for rowi in range(0,len(src_rows)):
            row = src_rows[rowi]
            #
            while len(row) > 0:
                chki = len(row) - 1
                chko = row[chki]
                if type(chko) == dict:
                    if "special" in chko:
                        spsh = chko["special"]
                        row.pop()
                        while len(src_special) <= rowi:
                            src_special.append(False)
                        src_special[rowi] = spsh
                        continue
                break
            #
            special = { }
            if rowi < len(src_special):
                special = src_special[rowi]
                if special == False:
                    special = { }
            # TODO: allow JSON encoded table rows to indicate special info
            #
            # translation: the SUPPRESS() syntax is just there to make sure it doesn't get accidentally interpreted as data, unwrap it
            if "suppress" in special:
                x = re.match(r'^SUPPRESS\(([^.\]]*)\)$',special["suppress"])
                if not x == None and len(x.groups()) > 0:
                    special["suppress"] = x.group(1)
                #
                nob = { }
                for ent in re.split(r'\|',special["suppress"]):
                    if ent == "":
                        continue
                    ei = ent.find("=")
                    if ei >= 0:
                        nval = re.split(r',',ent[ei+1:])
                        if len(nval) < 2:
                            nval = nval[0]
                        nob[ent[0:ei].lower()] = nval
                    else:
                        nob[ent.lower()] = True
                #
                special["suppress"] = nob
            #
            drowobj = { "columns present": src_cols_present.copy() }
            drowobj["special"] = special
            drowobj["entry tags"] = { }
            if "entry tag" in ji:
                drowobj["entry tags"][ji["entry tag"]] = { }
            if len(drowobj["entry tags"]) == 0: # nothing there?
                drowobj["entry tags"][""] = { } # signify no entry tag
            # the code below will append to sources, so the index to list is the length of the list NOW before appending
            if not source_obj == None:
                drowobj["source index"] = source_index
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
            tablerowtodatatype(basetablecols,drow,ji,drowobj)
            #
            drowar = tablerowrangeproc(basetablecols,drowobj)
            # SUPPRESS(ALL) means do not include the table at all
            if "suppress" in special and "all" in special["suppress"]:
                if not "suppressed" in table:
                    table["suppressed"] = [ ]
                table["suppressed"].append(drowar)
                continue
            #
            rows += drowar
    #
    ji["source json file"] = path
    for what in ["schema","table in csv","table","table special","table columns","base definition","table column array separator","table column range separator"]:
        if what in ji:
            del ji[what]
    table["sources"].append(ji)

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
    if type(col) == dict:
        r = [ ]
        if "value" in col:
            r = [ rowcolsortfilter(tcol,col["value"]) ]
        return r
    if type(col) == list:
        r = [ ]
        for scol in col:
            r.append(rowcolsortfilter(tcol,scol))
        return r
    #
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

def tablearraycombinedcoldedupsortfmt(ve):
    if "text" in ve:
        return ve["text"]
    if "sub" in ve:
        r = ""
        for subi in ve["sub"]:
            r += tablearraycombinedcoldedupsortfmt(subi)
        return r
    if "info" in ve:
        if "text" in ve["info"]:
            return ve["info"]["text"]
    if "fields" in ve:
        r = ""
        for key in ve["fields"]:
            r += key
            r += ve["fields"][key]
        return r
    return ""

def tablearraycombinedcoldedupsort(tcol,colent):
    r = [ ]
    if "value" in colent:
        v = colent["value"]
        if not type(v) == list:
            v = [ v ]
        for ve in v:
            if type(ve) == dict:
                ve = tablearraycombinedcoldedupsortfmt(ve)
            #
            if "case insensitive" in tcol and tcol["case insensitive"] == True and isinstance(ve,str):
                ve = ve.lower()
            #
            r.append(ve)
    return r

def tablearraycombinedcoldedupmergespecial(lmv,v):
    if not "special" in lmv:
        lmv["special"] = { }
    if not "suppress" in lmv["special"]:
        lmv["special"]["suppress"] = { }
    if not "special" in lmv:
        v["special"] = { }
    if not "suppress" in v["special"]:
        v["special"]["suppress"] = { }
    for sv in v["special"]["suppress"]:
        if sv in lmv["special"]["suppress"]:
            if not lmv["special"]["suppress"][sv] == v["special"]["suppress"][sv]:
                print(lmv["special"]["suppress"][sv])
                print(v["special"]["suppress"][sv])
                raise Exception("Conflicting suppress spec")
        else:
            lmv["special"]["suppress"][sv] = v["special"]["suppress"][sv]

def col_proc_pickone_spec(tcol,col):
    pick = None
    rejcol = [ ]
    pickcol = [ ]
    for cent in col:
        if not "special" in cent:
            rejcol.append(cent)
            continue
        spec = cent["special"]
        if not "suppress" in spec:
            rejcol.append(cent)
            continue
        supp = spec["suppress"]
        if len(supp) == 0:
            rejcol.append(cent)
            continue
        reject = True
        if "pickthis" in supp:
            pl = supp["pickthis"]
            if not type(pl) == list:
                pl = [ pl ]
            for plent in pl:
                if plent == tcol["name"]:
                    reject = False
                    if pick == None:
                        pick = plent
                        pickcol.append(cent)
                    elif pick == plent:
                        pickcol.append(cent)
                    else:
                        raise Exception("Conflicting pickthis spec vs "+plent)
        if reject == True:
            rejcol.append(cent)
    if not pick == None:
        col = pickcol
        col[0]["rejected pickone"] = rejcol
        for r in rejcol:
            col[0]["source index"] += r["source index"]
            for key in r["entry tags"]:
                col[0]["entry tags"][key] = r["entry tags"][key]
    #
    return col

def col_proc_this_spec(tcol,col,table):
    for cent in col:
        if not "special" in cent:
            continue
        spec = cent["special"]
        if not "suppress" in spec:
            continue
        supp = spec["suppress"]
        if len(supp) == 0:
            continue
        reject = True
        if "this" in supp:
            pl = supp["this"]
            if not type(pl) == list:
                pl = [ pl ]
            for plent in pl:
                if plent == tcol["name"]:
                    if plent in table["table name to column"]:
                        dcoli = table["table name to column"][plent]
                        if "value" in cent:
                            cent["suppressed:this"] = True
                            cent["value"] = ""

def tablearraycombinedcoldedup(tcol,col,table):
    def addit(dest_index,source_index,dest_entry_tags,source_entry_tags):
        dest_index += source_index
        for key in source_entry_tags:
            dest_entry_tags[key] = source_entry_tags[key]

    # any suppress pickone specs?
    col = col_proc_pickone_spec(tcol,col)
    # SUPPRESS(THIS=...)
    col_proc_this_spec(tcol,col,table)
    # sort the column values
    col.sort(key=lambda x: tablearraycombinedcoldedupsort(tcol,x))
    # then scan and dedup
    lmv = { }
    pv = { }
    r = [ ]
    pending_source_index = [ ]
    pending_entry_tags = { }
    for v in col:
        pvds = tablearraycombinedcoldedupsort(tcol,pv)
        vds = tablearraycombinedcoldedupsort(tcol,v)
        if vds == [ '' ] or vds == [ ]: # ignore empty columns
            if "suppressed:this" in v:
                addit(dest_index=pending_source_index,source_index=v["source index"],dest_entry_tags=pending_entry_tags,source_entry_tags=v["entry tags"])
            continue
        if not pvds == vds:
            r.append(v)
            lmv = v
            addit(dest_index=v["source index"],source_index=pending_source_index,dest_entry_tags=v["entry tags"],source_entry_tags=pending_entry_tags)
            pending_source_index = [ ]
            pending_entry_tags = { }
        else:
            addit(dest_index=lmv["source index"],source_index=v["source index"],dest_entry_tags=lmv["entry tags"],source_entry_tags=v["entry tags"])
            tablearraycombinedcoldedupmergespecial(lmv,v)
        pv = v
    #
    if len(lmv) > 0:
        addit(dest_index=lmv["source index"],source_index=pending_source_index,dest_entry_tags=lmv["entry tags"],source_entry_tags=pending_entry_tags)
        pending_source_index = [ ]
        pending_entry_tags = { }
    #
    col = r
    # sort source indexes
    for cv in col:
        cv["source index"].sort()
        pv = -1
        nv = [ ]
        for v in cv["source index"]:
            if not pv == v:
                nv.append(v)
            pv = v
        cv["source index"] = nv
    return col

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
            # anything marked combine different is ignored at this stage
            if "combine different" in tcols[coli] and tcols[coli]["combine different"] == True:
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
                if tcols[coli]["compiled format"] == "array/combined":
                    browdat[coli] += srowdat[coli]
            #
            buildrow["source index"] += srow["source index"]
            for key in srow["entry tags"]:
                buildrow["entry tags"][key] = srow["entry tags"][key]
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
        # array/combined too
        for coli in range(0,len(tcols)):
            if tcols[coli]["compiled format"] == "array/combined":
                row["data"][coli] = tablearraycombinedcoldedup(tcols[coli],row["data"][coli],table)
                for colent in row["data"][coli]:
                    if "special" in colent:
                        if "suppress" in colent["special"]:
                            if len(colent["special"]["suppress"]) == 0:
                                del colent["special"]["suppress"]
                        if len(colent["special"]) == 0:
                                del colent["special"]
        #
        if "special" in row:
            if "suppress" in row["special"]:
                if len(row["special"]["suppress"]) == 0:
                    del row["special"]["suppress"]
            if len(row["special"]) == 0:
                del row["special"]
    #
    table["rows"] = nrows

# process tables
for scan in get_base_tables():
    obj = { }
    # process base table
    procbasetable(scan,obj)
    # then process content tables and add to base table rows
    for content in get_content_tables(scan):
        proc_content_table(content,obj)
    # sort rows and dedup rows
    sorttable(obj)
    deduptable(obj)
    # write compiled JSON to file
    ji = obj["ji"]
    apodjson.write_json("compiled/tables/"+ji["id"]+".json",ji);

