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
    if v[0:2] == "0x":
        return int(v,base=16)
    return int(v)

class TableColProc:
    fromValue = None
    fromJsonKey = False
    fromType = None
    fromColumn = None
    defaultValue = None
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
        self.fromValue = col
    def scanf(self,v):
        if self.fromType == "uint8_t":
            return str2int(v)
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
    def format(self,key,row):
        colo = None
        ret = { }
        #
        for col in self.columnOrder:
            ret[col] = ""
            if col in self.columns:
                colo = self.columns[col]
                if not colo.defaultValue == None:
                    ret[col] = colo.scanf(colo.defaultValue)
                if colo.fromJsonKey == True:
                    ret[col] = colo.scanf(key)
        #
        for col in row:
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
            row = table_data[key]
            rowf = tablerowproc[ji["id"]].format(key,row)
            rowf["_source"] = path;
            tables[ji["id"]]["rows"].append(rowf)
    else:
        raise Exception("table data not in expected format")

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

write_json("compiled/tables.json",tables);

