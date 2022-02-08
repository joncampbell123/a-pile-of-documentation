#!/usr/bin/python3

import os
import glob
import json
import pathlib

import common_json_help_module

def dict_sorted_uint_func(a):
    return int(a,0)

def dict_sorted_text_func(a):
    return a.lower()

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
    #
    def build_table_key_value(self,json):
        self.display.colsiz = [ 1 ]
        self.display.colobj = [ self.key_column ]
        self.display.colhdr = [ self.key_column.get("title") ]
        self.display.coldesc = [ self.key_column.get("description") ]
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
                if len(rowbuild) > 0 and rowbuild[len(rowbuild)-1]["columns"] == newrowcols:
                    rowbuild[len(rowbuild)-1]["source index"].append(row.get("source index"))
                else:
                    samekey = False
                    if len(rowbuild) > 0:
                        if rowbuild[len(rowbuild)-1]["columns"][0] == newrowcols[0]:
                            samekey = True
                            rowbuild[len(rowbuild)-1]["same key"] = samekey
                    rowbuild.append( { "columns": newrowcols, "source index": [ row.get("source index") ], "same key": samekey } )
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
                    for ctxtlin in ctxt.split('\n'):
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

def emit_table_as_text(path,tp):
    #
    f = open(path,"w",encoding="UTF-8")
    f.write("\n")
    #
    f.write(tp.display.header+"\n")
    f.write(("="*len(tp.display.header))+"\n")
    f.write("\n")
    #
    if not tp.description == None:
        f.write(tp.description+"\n")
        f.write("\n")
    #
    if not tp.display.disptable == None:
        desci = 0
        for ci in range(len(tp.display.colsiz)):
            if not tp.display.colhdr[ci] == None and not tp.display.coldesc[ci] == None:
                x = tp.display.colhdr[ci] + ": " + tp.display.coldesc[ci]
                f.write(" - "+x+"\n")
                desci = desci + 1
        if desci > 0:
            f.write("\n")
        #
        for ci in range(len(tp.display.colsiz)):
            if ci > 0:
                f.write(" | ")
            x = ""
            if not tp.display.colhdr[ci] == None:
                x = tp.display.colhdr[ci]
            x = (x + (" "*tp.display.colsiz[ci]))[0:tp.display.colsiz[ci]]
            f.write(x)
        f.write("\n")
        #
        for ci in range(len(tp.display.colsiz)):
            if ci > 0:
                f.write("=|=")
            x = "="*tp.display.colsiz[ci]
            f.write(x)
        f.write("\n")
        #
        if len(tp.display.disptable) > 0:
            for row in tp.display.disptable:
                columns = row.get("columns")
                if not columns == None:
                    # NTS: array of arrays, because column values can have newlines
                    coltext = [ ]
                    collines = 1
                    # first pass: grab each column value, split by newline, stuff into coltext
                    for coli in range(len(columns)):
                        col = columns[coli]
                        val = col.get("value")
                        if val == None:
                            val = ""
                        #
                        vallines = val.split('\n')
                        coltext.append(vallines)
                        # how many vertical lines will this column need?
                        # to render correctly, all columns will be printed with this many vertical lines.
                        if collines < len(vallines):
                            collines = len(vallines)
                    # second pass: draw the columns, multiple lines if needed
                    for collc in range(collines):
                        for coli in range(len(columns)):
                            if coli > 0:
                                f.write(" | ")
                            #
                            val = ""
                            cola = coltext[coli]
                            if collc < len(cola):
                                val = cola[collc]
                                if val == None:
                                    val = ""
                            #
                            x = (val + (" "*tp.display.colsiz[coli]))[0:tp.display.colsiz[coli]]
                            f.write(x)
                        #
                        if collc == 0 and row.get("same key") == True:
                            sia = row.get("source index")
                            if not sia == None:
                                for si in sia:
                                    f.write(" [*"+str(si)+"]")
                        #
                        f.write("\n")
            #
            f.write("\n")
    #
    if not tp.sources == None:
        f.write("Sources\n")
        f.write("=======\n")
        for sii in range(len(tp.sources)):
            sobj = tp.sources[sii]
            if not int(sobj.get("source index")) == sii:
                raise Exception("source index is wrong")
            head = "  [*"+str(sii)+"] "
            f.write(head)
            if "book" in sobj:
                book = sobj["book"]
            elif "website" in sobj:
                book = sobj["website"]
            else:
                book = None

            if not book == None:
                where = sobj.get("where")
                citation = sobj.get("citation")
                if not citation == None:
                    x = ""
                    title = citation.get("title")
                    if not title == None:
                        if not x == "":
                            x = x + ", "
                        x = x + title
                    author = citation.get("author")
                    if not author == None:
                        if not x == "":
                            x = x + ", "
                        x = x + author
                    publisher = citation.get("publisher")
                    if not publisher == None:
                        if not x == "":
                            x = x + ", "
                        x = x + publisher
                    year = citation.get("year")
                    if not year == None:
                        if not x == "":
                            x = x + ", "
                        x = x + str(year)
                    if not x == "":
                        f.write(x+"\n")
                    #
                    url = citation.get("url")
                    if not url == None:
                        f.write(" "*len(head))
                        f.write("URL: "+url+"\n")
                if not where == None:
                    x = ""
                    for whi in where:
                        y = ""
                        if "path" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["path"]
                        if "title" in whi:
                            if not y == "":
                                y = y + ", "
                            y = y + whi["title"]
                        if not y == "":
                            if not x == "":
                                x = x + " => "
                            x = x + y
                    if not x == "":
                        f.write(" "*len(head))
                        f.write(x+"\n")
            #
            f.write("\n")
    #
    if not tp.notes == None:
        f.write("Notes\n")
        f.write("-----\n")
        for note in tp.notes:
            f.write(" * "+note+"\n")
        f.write("\n")
    #
    f.close()

os.system("rm -Rf reference/text/tables; mkdir -p reference/text/tables")

tables_json = common_json_help_module.load_json("compiled/tables.json")

tables = tables_json.get("tables")
if not tables == None:
    for table_id in tables:
        tp = TablePresentation(tables[table_id])
        emit_table_as_text("reference/text/tables/"+table_id+".txt",tp)

