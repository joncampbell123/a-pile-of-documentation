
import os
import re
import glob
import json
import pathlib

def dict_sorted_uint_func(a):
    return int(a,0)

def dict_sorted_text_func(a):
    return a.lower()

def dict_sorted_mixed_func(a):
    ca = a.split(" ")
    for i in range(len(ca)):
        ca[i] = ca[i].lower()
        if re.match(r"^[0-9]+$",ca[i]) or re.match(r"^0x[0-9a-f]+$",ca[i]):
            ca[i] = int(ca[i],0)
    return ca

def rowbuild_sort(a):
    r = [ ]
    for co in a["columns"]:
        v = ""
        if "value" in co:
            v = co["value"]
        r.append(v)
    #
    r.append(a["source index"])
    #
    return r

class TablePresentation:
    name = None
    notes = None
    table = None
    sources = None
    columns = None
    display = None
    base_json = None
    key_column = None
    description = None
    table_format_type = None
    #
    class DisplayInfo:
        disptable = [ ]
        header = None
        colsiz = None
        colhdr = None
        colobj = None
        coldesc = None
        columns_have_newlines = False
    #
    def build_table_key_value(self,json):
        self.display.colsiz = [ 1 ]
        self.display.colobj = [ self.key_column ]
        self.display.colhdr = [ self.key_column.get("title") ]
        self.display.coldesc = [ self.key_column.get("description") ]
        self.display.columns_have_newlines = False
        #
        for col in self.columns:
            self.display.colsiz.append(1)
            self.display.colobj.append(col)
            self.display.colhdr.append(col.get("title"))
            self.display.coldesc.append(col.get("description"))
        #
        for coli in range(len(self.display.colhdr)):
            cht = self.display.colhdr[coli]
            if cht == None:
                cht = ""
            clen = len(cht)
            if self.display.colsiz[coli] < clen:
                self.display.colsiz[coli] = clen
        #
        sortFunc = None
        if not self.key_column == None:
            if self.key_column["type"][0:4] == "uint":
                sortFunc = dict_sorted_uint_func
            if self.key_column["type"][0:6] == "string":
                sortFunc = dict_sorted_text_func
            if self.key_column["type"][0:5] == "mixed":
                sortFunc = dict_sorted_mixed_func
        #
        self.display.disptable = [ ]
        for rowkey in sorted(self.table,key=sortFunc):
            rowent = self.table[rowkey]
            #
            key = rowkey
            for row in rowent:
                if "original key" in row:
                    key = row["original key"]
                    break
            #
            rowbuild = [ ]
            for row in rowent:
                newrowcols = [ { "value": key } ]
                #
                value = row.get("value")
                if not isinstance(value,list):
                    value = [ value ]
                #
                for coli in range(len(self.columns)):
                    col = self.columns[coli]
                    newrowcols.append({ "value": value[coli] })
                #
                rowbuild.append( { "columns": newrowcols, "source index": [ row.get("source index") ] } )
            #
            rowbuild = sorted(rowbuild,key=rowbuild_sort)
            #
            nr = [ ]
            pcols = None
            samekey = False
            #
            if len(self.sources) > 1:
                samekey = True
            #
            for row in rowbuild:
                if pcols == None:
                    nr.append(row)
                elif pcols["columns"] == row["columns"]:
                    pcols["source index"].extend(row["source index"])
                else:
                    nr.append(row)
                #
                pcols = row
            rowbuild = nr
            #
            if samekey == True:
                for row in rowbuild:
                    row["same key"] = True
            #
            self.display.disptable.extend(rowbuild)
        #
        for row in self.display.disptable:
            if "columns" in row:
                columns = row["columns"]
                for coli in range(len(columns)):
                    cobj = columns[coli]
                    ctxt = cobj.get("value")
                    if ctxt == None:
                        ctxt = ""
                    # Problem: The text may have newlines! Split by newline then use the longest line
                    ctxtlines = ctxt.split('\n')
                    if len(ctxtlines) > 1:
                        self.display.columns_have_newlines = True
                    for ctxtlin in ctxtlines:
                        clen = len(ctxtlin)
                        if self.display.colsiz[coli] < clen:
                            self.display.colsiz[coli] = clen
    #
    def __init__(self,json):
        self.base_json = json
        self.table = json.get("table")
        self.sources = json.get("sources")
        self.description = json.get("description")
        self.table_format_type = json.get("table format type")
        self.key_column = json.get("key column")
        self.columns = json.get("columns")
        self.notes = json.get("notes")
        self.name = json.get("name")
        #
        self.display = TablePresentation.DisplayInfo()
        self.display.header = self.name
        if self.display.header == None:
            self.display.header = "Untitled"
        #
        self.display.colsiz = [ ]
        self.display.colhdr = [ ]
        self.display.colobj = [ ]
        self.display.coldesc = [ ]
        #
        if not self.table == None:
            if self.table_format_type == "key=value":
                self.build_table_key_value(json)

