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
tables = { }
tablerowproc = { }

def str2int(v):
    if v == "-":
        return v
    if v[0:2] == "0x":
        return int(v,base=16)
    return int(v)

class TableColProc:
    fromValue = None
    fromJsonKey = False
    fromType = None
    fromColumn = None
    defaultValue = None
    caseInsensitive = False
    combineDifferent = False
    stringSort = None
    def __init__(self,row,tcol_json,col):
        if "type" in tcol_json:
            self.fromType = tcol_json["type"]
        else:
            self.fromType = "string"
        #
        if "column" in tcol_json:
            self.fromColumn = tcol_json["column"]
        #
        if "json" in tcol_json:
            self.fromJsonKey = tcol_json["json"] == "key"
        #
        if "default" in tcol_json:
            self.defaultValue = tcol_json["default"]
        #
        if "case insensitive" in tcol_json:
            self.caseInsensitive = tcol_json["case insensitive"] == True
        #
        if "combine different" in tcol_json:
            self.combineDifferent = tcol_json["combine different"] == True
        #
        if "string sort" in tcol_json:
            self.stringSort = tcol_json["string sort"];
        #
        self.fromValue = col
    def scanf(self,v):
        if self.fromType == "bool":
            if isinstance(v,bool):
                return v
            if v == "true" or v == "1" or v > 0:
                return True
            if v == "false" or v == "0" or v <= 0:
                return False
            return False
        if self.fromType == "uint8_t" or self.fromType == "uint_t":
            return str2int(v)
        if self.fromType == "string" and self.combineDifferent == True:
            v = { "_string": v }
        return v
    def sortfilter(self,v):
        if self.fromType == "string" and self.caseInsensitive == True:
            if type(v) == dict:
                if "_string" in v:
                    v = v["_string"].lower()
                else:
                    v = ""
            else:
                v = v.lower()
        if self.fromType == "string":
            if self.stringSort == "numeric":
                nv = [ ]
                for e in re.findall('\d+|[^\d]+',v):
                    if re.search('^\d+$',e):
                        nv.append(str2int(e))
                    else:
                        nv.append(e)
                return nv
        if self.fromType[0:4] == "uint":
            if v == "-":
                return 0 # allow - but make fake number
        return v

class TableRowProc:
    columns = None
    columnOrder = None
    def __init__(self,table_json):
        self.columnOrder = [ ]
        if "table format" in table_json:
            tf = table_json["table format"]
            if "order" in tf:
                self.columnOrder = tf["order"]
                if not type(self.columnOrder) == list:
                    raise Exception("table order not list")
        #
        self.columns = { }
        if "table columns" in table_json:
            tc = table_json["table columns"]
            if not type(tc) == dict:
                raise Exception("table columns not dict")
            for col in tc:
                if col in self.columns:
                    raise Exception(col+" already exists in columns")
                self.columns[col] = TableColProc(self,tc[col],col)
    def rowsortfunc(self,val):
        ar = [ ]
        for col in self.columnOrder:
            v = ""
            if col in val:
                v = val[col]
            if col in self.columns:
                colo = self.columns[col]
                v = colo.sortfilter(v)
            ar.append(v)
        #
        return ar
    def dedupsortfunc(self,val):
        ar = [ ]
        for col in self.columnOrder:
            v = ""
            if col in val:
                v = val[col]
            if col in self.columns:
                colo = self.columns[col]
                if colo.combineDifferent:
                    v = ''
                else:
                    v = colo.sortfilter(v)
            ar.append(v)
        #
        return ar
    def combinerows(self,acrow,scrow):
        # combine the contents of any column marked combine contents
        for col in self.columnOrder:
            if not col in scrow:
                continue
            if not col in self.columns:
                continue
            colo = self.columns[col]
            if colo.combineDifferent == True:
                if colo.fromType == "string":
                    if acrow[col] == None:
                        acrow[col] = scrow[col]
                    else:
                        if not type(acrow[col]) == list:
                            acrow[col] = [ acrow[col] ]
                        acrow[col].append(scrow[col])
        # always combine the _source list
        if "_source" in acrow and "_source" in scrow:
            if not type(acrow["_source"]) == list:
                acrow["_source"] = [ acrow["_source"] ]
            acrow["_source"].append(scrow["_source"])
        return acrow
    def format(self,key,row):
        colo = None
        ret = { }
        #
        for col in self.columnOrder:
            ret[col] = ""
            if col in self.columns:
                colo = self.columns[col]
                if colo.fromJsonKey == True:
                    ret[col] = colo.scanf(key)
                elif not colo.defaultValue == None:
                    ret[col] = colo.scanf(colo.defaultValue)
                elif colo.fromType == "string":
                    ret[col] = colo.scanf("")
        #
        for col in row:
            colo = None
            if col in self.columns:
                colo = self.columns[col]
            if not colo == None:
                ret[col] = colo.scanf(row[col])
            else:
                ret[col] = row[col]
        #
        return ret

# process, first base definitions
g = glob.glob("tables/**/*--base.json",recursive=True)
for path in g:
    ji = load_json(path)
    if not "id" in ji:
        continue
    if not "base definition" in ji:
        continue
    if not ji["base definition"] == True:
        raise Exception("base json that is not base definition")
    if ji["id"] in tables:
        raise Exception("table "+ji["id"]+" already exists")
    #
    ji["source json file"] = path
    #
    ji["sources"] = { }
    ji["rows"] = [ ]
    #
    tables[ji["id"]] = ji;
    tablerowproc[ji["id"]] = TableRowProc(ji)

# table row postprocessing
def table_row_postprocess(ji,rtrow):
    nrows = [ ]
    if type(rtrow) == list:
        for irtrow in rtrow:
            nrows.extend(table_row_postprocess(ji,irtrow))
    elif "_columns" in rtrow:
        cols = { }
        scols = rtrow["_columns"]
        if not "table value column order" in ji:
            raise Exception("_columns without table value column order")
        colnames = ji["table value column order"]
        if not type(colnames) == list:
            raise Exception("table value column order must be list")
        if not type(scols) == list:
            raise Exception("_columns must be list")
        for coli in range(0,len(scols)):
            colval = scols[coli]
            colname = colnames[coli]
            if colname in cols:
                raise Exception("Duplicate column")
            cols[colname] = colval
        nrows.append(cols)
    else:
        nrows.append(rtrow)
    #
    return nrows

# process, tables
g = glob.glob("tables/**/*.json",recursive=True)
for path in g:
    ji = load_json(path)
    if not "id" in ji:
        continue
    if "base definition" in ji:
        if ji["base definition"] == True:
            continue
    if not ji["id"] in tables:
        raise Exception("table "+ji["id"]+" does not exist")
    if not ji["id"] in tablerowproc:
        raise Exception("table "+ji["id"]+" processing not init")
    #
    ji["source json file"] = path
    # extract table, remove from source JSON object
    if "table" in ji:
        table_data = ji["table"]
        del ji["table"]
    else:
        continue
    #
    tables[ji["id"]]["sources"][path] = ji
    # process table rows and add to table
    if type(table_data) == dict:
        for key in table_data:
            for row in table_row_postprocess(ji,table_data[key]):
                rowf = tablerowproc[ji["id"]].format(key,row)
                #
                for colname in rowf:
                    if colname in tablerowproc[ji["id"]].columns:
                        colo = tablerowproc[ji["id"]].columns[colname]
                        if colo.fromType == "string" and colo.combineDifferent:
                            if type(rowf[colname]) == dict:
                                rowf[colname]["_source"] = path;
                #
                rowf["_source"] = path;
                tables[ji["id"]]["rows"].append(rowf)
    else:
        raise Exception("table data not in expected format")

def combinestrobjsort(v):
    if type(v) == dict:
        if "_string" in v:
            return v["_string"]
        return ""
    return v

def combinedupcombinestr(cols):
    ncols = [ ]
    acidx = 0
    scidx = 1
    while scidx < len(cols):
        if acidx >= scidx:
            raise Exception("Processing error")
        #
        accol = cols[acidx]
        sccol = cols[scidx]
        if not type(accol) == dict:
            raise Exception("not dict")
        if not type(sccol) == dict:
            raise Exception("not dict")
        if not "_string" in accol:
            raise Exception("no string")
        if not "_string" in sccol:
            raise Exception("no string")
        #
        if accol["_string"] == sccol["_string"]:
            if "_source" in sccol:
                if not "_source" in accol:
                    accol["_source"] = [ ]
                if not type(accol["_source"]) == list:
                    accol["_source"] = [ accol["_source"] ]
                accol["_source"].append(sccol["_source"])
        else:
            ncols.append(accol)
            acidx = scidx
        #
        scidx = scidx + 1
    #
    if acidx < scidx:
        ncols.append(cols[acidx])
    # an array of one should become the object itself
    if len(ncols) == 1:
        ncols = ncols[0]
    #
    return ncols

def table_dedup_combine(table,tproc,rows):
    nrows = [ ]
    if len(rows) > 0:
        acidx = 0
        scidx = 1
        while scidx < len(rows):
            if acidx >= scidx:
                raise Exception("Processing error")
            #
            acrow = rows[acidx]
            scrow = rows[scidx]
            if tproc.dedupsortfunc(acrow) == tproc.dedupsortfunc(scrow):
                tproc.combinerows(acrow,scrow) # combine, dedup contents (pass by reference)
            else:
                nrows.append(acrow) # flush combined row,
                acidx = scidx # begin accumulating on this row
            #
            scidx = scidx + 1
        #
        if acidx < scidx:
            nrows.append(rows[acidx])
    # sometimes this processing causes multiple redundant _source entries
    for row in rows:
        if "_source" in row:
            rowsrc = row["_source"]
            if type(rowsrc) == list:
                rowsrc.sort()
                nr = [ ]
                pe = None
                for ce in rowsrc:
                    if not ce == pe:
                        nr.append(ce)
                    pe = ce
                row["_source"] = nr
        #
        for colname in tproc.columns:
            if not colname in row:
                continue
            rcol = row[colname]
            colo = tproc.columns[colname]
            if colo.fromType == "string" and colo.combineDifferent:
                if type(rcol) == list:
                    rcol.sort(key=combinestrobjsort)
                    rcol = row[colname] = combinedupcombinestr(rcol)
    #
    return nrows

# sort all table rows
for tid in tables:
    table = tables[tid]
    tproc = tablerowproc[tid]
    rows = table["rows"]
    rows.sort(key=tproc.rowsortfunc)
    # then remove or combine duplicate or redundant data, which is easy now the data is sorted
    table["rows"] = rows = table_dedup_combine(table,tproc,rows)

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")
if not os.path.exists("compiled/tables"):
    os.mkdir("compiled/tables")

# the information is going to grow, eventually get very large.
# let's put each table in separate files to avoid very large JSON files.
for tablename in tables:
    write_json("compiled/tables/"+tablename+".json",tables[tablename]);

