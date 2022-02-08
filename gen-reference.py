#!/usr/bin/python3

import os
import glob
import json
import pathlib

import common_json_help_module
import table_presentation_module

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
                        show_sources = False
                        if collc == 0 and row.get("same key") == True:
                            show_sources = True
                        #
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
                            #
                            if not show_sources == True and coli == len(columns) - 1:
                                x = x.rstrip()
                            #
                            f.write(x)
                        #
                        if show_sources == True:
                            sia = row.get("source index")
                            if not sia == None:
                                for si in sia:
                                    f.write(" [*"+str(si)+"]")
                        #
                        f.write("\n")
                    # Problem: If any column has multiple lines, the per-line text format becomes confusing, and lines are needed to visually separate them
                    if tp.display.columns_have_newlines == True:
                        for ci in range(len(tp.display.colsiz)):
                            if ci > 0:
                                f.write("-+-")
                            x = "-"*tp.display.colsiz[ci]
                            f.write(x)
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

def html_escape(e):
    r = ""
    for c in e:
        if c == '&':
            r = r + "&amp;"
        elif c == '<':
            r = r + "&lt;"
        elif c == '>':
            r = r + "&gt;"
        elif c == '"':
            r = r + "&quot;"
        elif c == '\'':
            r = r + "&apos;"
        else:
            r = r + c
    #
    return r

def emit_table_as_html(path,tp):
    #
    title = tp.display.header
    #
    f = open(path,"w",encoding="UTF-8")
    f.write("<!DOCTYPE HTML>\n")
    f.write("<html>")
    #
    f.write("<head>")
    f.write("<meta charset=\"utf-8\">")
    f.write("<title>"+html_escape(title)+"</title>")
    f.write("</head>")
    #
    f.write("<body>");
    f.write("<h2><span style=\"border-bottom: double;\">"+html_escape(title)+"</span></h2>")
    #
    if not tp.description == None:
        f.write("<p>"+html_escape(tp.description)+"</p>")
    #
    if not tp.display.disptable == None:
        desci = 0
        for ci in range(len(tp.display.colsiz)):
            if not tp.display.colhdr[ci] == None and not tp.display.coldesc[ci] == None:
                if desci == 0:
                    f.write("<table>")
                f.write("<tr>")
                f.write("<td style=\"font-weight: 700; padding-right: 1em; white-space: pre;\">"+html_escape(tp.display.colhdr[ci])+":</td>")
                f.write("<td>"+html_escape(tp.display.coldesc[ci])+"</td>")
                f.write("</tr>")
                desci = desci + 1
        if desci > 0:
            f.write("</table><br>")
        #
        f.write("<table style=\"border: 1px solid black; border-spacing: 0px;\">")
        #
        f.write("<tr style=\"background-color: rgb(224,224,224);\">")
        for ci in range(len(tp.display.colsiz)):
            x = ""
            if not tp.display.colhdr[ci] == None:
                x = tp.display.colhdr[ci]
            #
            if ci == len(tp.display.colsiz)-1:
                style = ""
            else:
                style = "border-right: 1px solid black;"
            #
            style = style + " padding: 0.2em; padding-right: 1em;"
            style = style + " border-bottom: 1px solid black; font-size: 0.9em; text-align: left;"
            #
            f.write("<th style=\""+style.strip()+"\">"+html_escape(x)+"</th>")
        f.write("</tr>")
        #
        if len(tp.display.disptable) > 0:
            for rowidx in range(len(tp.display.disptable)):
                row = tp.display.disptable[rowidx]
                columns = row.get("columns")
                if not columns == None:
                    f.write("<tr valign=\"top\">")
                    show_sources = False
                    # HTML can handle multi-line just fine for us
                    for coli in range(len(columns)):
                        #
                        col = columns[coli]
                        val = col.get("value")
                        if val == None:
                            val = ""
                        #
                        if row.get("same key") == True:
                            show_sources = True
                        #
                        f.write("<td style=\"")
                        f.write("white-space: pre; padding: 0.2em; padding-right: 1em; font-size: 0.9em; text-align: left;")
                        if not coli == len(columns)-1:
                            f.write(" border-right: 1px solid black;")
                        if not rowidx == len(tp.display.disptable)-1:
                            f.write(" border-bottom: 1px solid black;")
                        f.write("\">")
                        #
                        f.write(html_escape(val))
                        #
                        if coli == len(columns)-1 and show_sources == True:
                            sia = row.get("source index")
                            if not sia == None:
                                for si in sia:
                                    f.write("<sup style=\"color: rgb(0,0,192);\"><i> [*"+str(si)+"]</i></sup>")
                        #
                        f.write("</td>")
                    #
                    f.write("</tr>")
            #
            f.write("\n")
        #
        f.write("</table>")
    #
    f.write("</body>");
    #
    f.write("</html>")
    f.close()

os.system("rm -Rf reference/text/tables; mkdir -p reference/text/tables")
os.system("rm -Rf reference/html/tables; mkdir -p reference/html/tables")

tables_json = common_json_help_module.load_json("compiled/tables.json")

tables = tables_json.get("tables")
if not tables == None:
    for table_id in tables:
        tp = table_presentation_module.TablePresentation(tables[table_id])
        emit_table_as_text("reference/text/tables/"+table_id+".txt",tp)
        emit_table_as_html("reference/html/tables/"+table_id+".htm",tp)

