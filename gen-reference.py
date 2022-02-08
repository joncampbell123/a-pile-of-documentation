#!/usr/bin/python3

import os
import glob
import json
import pathlib

import common_json_help_module

def emit_table_as_text(path,table_id_json):
    table = table_id_json.get("table")
    sources = table_id_json.get("sources")
    description = table_id_json.get("description")
    table_format_type = table_id_json.get("table format type")
    key_column = table_id_json.get("key column")
    columns = table_id_json.get("columns")
    notes = table_id_json.get("notes")
    name = table_id_json.get("name")
    #
    f = open(path,"w",encoding="UTF-8")
    f.write("\n")
    #
    hdr = name
    if hdr == None:
        hdr = "Untitled table"
    f.write(hdr+"\n")
    f.write(("="*len(hdr))+"\n")
    f.write("\n")
    #
    if not description == None:
        f.write(description+"\n")
        f.write("\n")
    #
    if not table == None:
        if table_format_type == "key=value":
            colsiz = [ 1 ]
            colhdr = [ None ]
            if not key_column == None:
                colhdr[0] = key_column
                if not colhdr[0] == None:
                    if "title" in colhdr[0]:
                        keyl = len(colhdr[0]["title"])
                        if colsiz[0] < keyl:
                            colsiz[0] = keyl
            #
            for col in columns:
                colhdr.append(col)
                colsiz.append(1)
            #
            for rowkey in table:
                row = table[rowkey]
                keyl = len(rowkey)
                if colsiz[0] < keyl:
                    colsiz[0] = keyl
                if len(columns) > 0:
                    colhdr[1] = columns[0]
                    #
                    if not colhdr[1] == None:
                        if "title" in colhdr[1]:
                            keyl = len(colhdr[1]["title"])
                            if colsiz[1] < keyl:
                                colsiz[1] = keyl
                    #
                    for sii in range(len(row)):
                        val = row[sii]
                        key = val.get("original key")
                        if key == None:
                            key = rowkey
                        keyl = len(key)
                        if colsiz[0] < keyl:
                            colsiz[0] = keyl
                        val = val.get("value")
                        if val == None:
                            val = ""
                        vall = len(val)
                        if colsiz[1] < vall:
                            colsiz[1] = vall
            #
            desci = 0
            for ci in range(len(colsiz)):
                col = colhdr[ci]
                if "title" in col and "description" in col:
                    f.write(" - "+col["title"]+": "+col["description"]+"\n")
                    desci = desci + 1
            if desci > 0:
                f.write("\n")
            #
            for ci in range(len(colsiz)):
                if ci > 0:
                    f.write(" | ")
                x = ""
                if not colhdr[ci] == None:
                    if "title" in colhdr[ci]:
                        x = colhdr[ci]["title"]
                x = (x + (" "*colsiz[ci]))[0:colsiz[ci]]
                f.write(x)
            f.write("\n")
            #
            for ci in range(len(colsiz)):
                if ci > 0:
                    f.write("=|=")
                x = "="*colsiz[ci]
                f.write(x)
            f.write("\n")
            #
            for rowkey in table:
                row = table[rowkey]
                key = rowkey
                disprows = [ ]
                dispsrcs = [ ]
                if len(row) > 0:
                    chkrow = row[0]
                    disprows.append(chkrow)
                    dispsrcs.append([ chkrow.get("source index") ])
                    for i in range(1,len(row)):
                        currow = row[i]
                        dif = False
                        if not currow.get("value") == chkrow.get("value"):
                            dif = True
                        #
                        if dif == True:
                            chkrow = currow
                            disprows.append(chkrow)
                            dispsrcs.append([ chkrow.get("source index") ])
                        else:
                            dispsrcs[len(dispsrcs)-1].append(currow.get("source index"))
                #
                for rowi in range(len(disprows)):
                    row = disprows[rowi]
                    x = rowkey
                    if "original key" in row:
                        x = row["original key"]
                    x = (x + (" "*colsiz[0]))[0:colsiz[0]]
                    f.write(x)
                    #
                    f.write(" | ")
                    #
                    x = ""
                    if "value" in row:
                        x = row["value"]
                    x = (x + (" "*colsiz[1]))[0:colsiz[1]]
                    f.write(x)
                    #
                    if len(disprows) > 1:
                        for si in dispsrcs[rowi]:
                            f.write(" [*"+str(si)+"]")
                    #
                    f.write("\n")
            #
            f.write("\n")
    #
    if not notes == None:
        f.write("Notes\n")
        f.write("-----\n")
        for note in notes:
            f.write(" * "+note+"\n")
        f.write("\n")
    #
    f.close()

os.system("rm -Rf reference/text/tables; mkdir -p reference/text/tables")

tables_json = common_json_help_module.load_json("compiled/tables.json")

tables = tables_json.get("tables")
if not tables == None:
    for table_id in tables:
        emit_table_as_text("reference/text/tables/"+table_id+".txt",tables[table_id])

