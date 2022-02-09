#!/usr/bin/python3

import os
import glob
import json
import pathlib

import common_json_help_module
import table_presentation_module

def emit_table_as_text(path,table_id,tp):
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
    if not tp.notes == None and len(tp.notes) > 0:
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

def emit_table_as_html(path,table_id,tp):
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
                f.write("<tr style=\"font-size: 0.9em;\">")
                f.write("<td style=\"font-weight: 700; padding-right: 1em; white-space: pre; text-align: left;\">"+html_escape(tp.display.colhdr[ci])+":</td>")
                f.write("<td style=\"text-align: left;\">"+html_escape(tp.display.coldesc[ci])+"</td>")
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
                                    f.write(" <a style=\"text-decoration: none;\" href=\"#"+table_id+"_source_"+str(si)+"\"><sup style=\"color: rgb(0,0,192);\"><i>[*"+str(si)+"]</i></sup></a>")
                        #
                        f.write("</td>")
                    #
                    f.write("</tr>")
            #
            f.write("\n")
        #
        f.write("</table>")
    #
    if not tp.sources == None:
        f.write("<p><span style=\"border-bottom: solid; border-bottom-width: thin;\">Sources</span></p>\n")
        f.write("<table style=\"font-size: 0.8em;\">")
        for sii in range(len(tp.sources)):
            f.write("<tr valign=\"top\">")
            sobj = tp.sources[sii]
            if not int(sobj.get("source index")) == sii:
                raise Exception("source index is wrong")
            #
            f.write("<td style=\"padding-left: 2em; padding-bottom: 1em;\" id=\""+table_id+"_source_"+str(sii)+"\"><sup style=\"color: rgb(0,0,192);\"><i>[*"+str(sii)+"]</i></sup></td>")
            #
            if "book" in sobj:
                book = sobj["book"]
            elif "website" in sobj:
                book = sobj["website"]
            else:
                book = None

            f.write("<td style=\"padding-bottom: 1em;\">")
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
                        f.write(html_escape(x)+"<br>")
                    #
                    url = citation.get("url")
                    if not url == None:
                        f.write("URL: <a href=\""+url+"\" target=\"_blank\">"+html_escape(url)+"</a><br>")
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
                        f.write(html_escape(x)+"<br>")
            f.write("</td>")
            #
            f.write("</tr>")
        #
        f.write("</table>")
    #
    if not tp.notes == None and len(tp.notes) > 0:
        f.write("<p><span style=\"border-bottom: solid; border-bottom-width: thin;\">Notes</span></p>")
        f.write("<ul style=\"font-size: 0.8em;\">")
        for note in tp.notes:
            f.write("<li>"+html_escape(note)+"</li>")
        f.write("</ul>")
    #
    f.write("</body>");
    #
    f.write("</html>")
    f.close()

# the world's simplest PDF generator class
class PDFGen:
    class PDFName:
        name = None
        def __init__(self,name):
            self.name = name
        def __str__(self):
            return self.name
    class PDFIndirect:
        id = None
        def __init__(self,id):
            if not type(id) == int:
                raise Exception("PDFIndirect id must be integer")
            self.id = id
    class PDFStream:
        data = None
        def __init__(self,data):
            self.data = data
    class Object:
        id = None
        value = None
        type = None # boolean, integer, real, text string, hex string, name, array, dict, stream, null, indirect
        def __init__(self,value=None,*,vtype=None):
            self.type = None
            self.set(value,vtype=vtype)
        def set(self,value=None,*,vtype=None):
            if vtype == None:
                if type(value) == bool:
                    vtype = bool
                elif type(value) == int:
                    vtype = int
                elif type(value) == float:
                    vtype = float
                elif type(value) == str:
                    vtype = str
                elif type(value) == bytes:
                    vtype = bytes
                elif type(value) == PDFGen.PDFName:
                    vtype = PDFGen.PDFName
                elif type(value) == list:
                    vtype = list
                elif type(value) == dict:
                    vtype = dict
                elif type(value) == PDFGen.PDFStream:
                    vtype = PDFGen.PDFStream
                elif value == None:
                    vtype = None
                elif type(value) == PDFGen.PDFIndirect:
                    vtype = PDFGen.PDFIndirect
                else:
                    raise Exception("Unable to determine type")
            #
            self.type = vtype
            if vtype == None:
                self.value = None
            elif vtype == bool:
                self.value = (value == True)
            elif vtype == int:
                if type(value) == int:
                    self.value = value
                else:
                    self.value = int(str(value),0)
            elif vtype == float:
                if type(value) == float:
                    self.value = value
                else:
                    self.value = float(str(value))
            elif vtype == str:
                if type(value) == str:
                    self.value = value
                else:
                    self.value = str(value)
            elif vtype == bytes:
                if type(value) == bytes:
                    self.value = value
                else:
                    raise Exception("bytes must be bytes")
            elif vtype == PDFGen.PDFName:
                if type(value) == str:
                    self.value = PDFGen.PDFName(value)
                elif type(value) == PDFGen.PDFName:
                    self.value = value
                else:
                    raise Exception("PDFName must be PDFName")
            elif vtype == list:
                if type(value) == list:
                    self.value = value
                else:
                    raise Exception("list must be list")
            elif vtype == dict:
                if type(value) == dict:
                    self.value = value
                else:
                    raise Exception("dict must be dict")
            elif vtype == PDFGen.PDFStream:
                if type(value) == bytes:
                    self.value = PDFGen.PDFStream(value)
                elif type(value) == PDFGen.PDFStream:
                    self.value = value
                else:
                    raise Exception("PDFStream must be PDFStream")
            elif vtype == None:
                if value == None:
                    self.value = value
                else:
                    raise Exception("None must be none")
            elif vtype == PDFGen.PDFIndirect:
                if type(value) == int:
                    self.value = PDFGen.PDFIndirect(value)
                elif type(value) == PDFGen.PDFIndirect:
                    self.value = value
                else:
                    raise Exception("PDFIndirect must be PDFIndirect")
            else:
                raise Exception("Don't know how to handle type "+str(vtype)+" value "+str(value))
    #
    pdfver = None
    objects = None
    #
    def __init__(self,optobj=None):
        self.pdfver = [ 1, 4 ]
        self.objects = [ None ] # object 0 is always NULL because most PDFs seem to count from 1
    #
    def new_object(self,value=None,*,vtype=None):
        id = len(self.objects)
        obj = PDFGen.Object(value,vtype=vtype)
        self.objects.append(obj)
        obj.id = id
        return obj
    #
    def pdf_str_escape(self,v):
        r = ""
        for c in v:
            if c == '\n':
                r = r + "\\n"
            elif c == '\r':
                r = r + "\\r"
            elif c == '\t':
                r = r + "\\t"
            elif c == '\b':
                r = r + "\\b"
            elif c == '\f':
                r = r + "\\f"
            elif c == '(':
                r = r + "\\("
            elif c == ')':
                r = r + "\\)"
            elif c == '\\':
                r = r + "\\\\"
            else:
                r = r + c
        #
        return r
    #
    def serialize(self,obj):
        if not type(obj) == PDFGen.Object:
            obj = PDFGen.Object(obj)
        #
        if obj.type == bool:
            if obj.value == True:
                return "true"
            else:
                return "false"
        elif obj.type == int:
            return str(obj.value)
        elif obj.type == float:
            return str(obj.value)
        elif obj.type == str:
            return "("+self.pdf_str_escape(obj.value)+")"
        elif obj.type == bytes:
            return "" # TODO
        elif obj.type == PDFGen.PDFName:
            return "/" + str(obj.value.name)
        elif obj.type == list:
            r = "["
            for ent in obj.value:
                r = r + " " + self.serialize(ent)
            r = r + " ]"
            return r
        elif obj.type == dict:
            r = "<<\n"
            for key in obj.value:
                objval = obj.value[key]
                r = r + self.serialize(key) + " " + self.serialize(objval) + "\n"
            r = r + " >>"
            return r
        elif obj.type == PDFGen.PDFStream:
            return "" # TODO
        elif obj.type == None:
            return "null"
        elif obj.type == PDFGen.PDFIndirect:
            return str(obj.value.id)+" 0 R"
        else:
            raise Exception("Unknown type on serialize")
    #
    def write_file(self,f):
        objofs = [ ]

        f.seek(0)
        f.write("%PDF-"+str(self.pdfver[0])+"."+str(self.pdfver[1])+"\n")
        f.write("\xf0\xf1\xf2\xf3\xf4\xf5\n\n") # non-ASCII chars to convince other programs this is not text
        for objid in range(len(self.objects)):
            obj = self.objects[objid]
            if not obj == None:
                if not obj.id == objid:
                    raise Exception("Object has wrong id")
            #
            if obj == None:
                if len(objofs) == objid:
                    objofs.append(None)
                else:
                    raise Exception("objid count error")
                continue
            elif not type(obj) == PDFGen.Object:
                raise Exception("PDF object list contains not a PDF object, instead is type "+str(type(obj)))
            #
            if len(objofs) == objid:
                objofs.append(f.tell())
            else:
                raise Exception("objid count error")
            #
            f.write(str(objid)+" 0 obj\n")
            f.write(self.serialize(obj))
            f.write("\n")
            f.write("endobj\n\n")
        #
        xrefofs = f.tell()
        f.write("xref\n")
        f.write("0 "+str(len(self.objects))+"\n")
        for objid in range(len(self.objects)):
            ofs = objofs[objid]
            if not ofs == None:
                s = str(ofs)[0:10]
                if len(s) < 10:
                    s = ("0"*(10-len(s)))+s
                f.write(s+" 00000 n\n")
            else:
                f.write("0000000000 65536 f\n")
        f.write("\n")
        #
        f.write("trailer\n")
        f.write("<<\n")
        f.write("  /Size "+str(len(self.objects))+"\n")
        f.write("  /Root 1 0 R\n") # TODO: Allow caller to set root node
        f.write(">>\n")
        #
        f.write("startxref\n")
        f.write(str(xrefofs)+"\n")
        f.write("%%EOF\n")

def emit_table_as_pdf(path,table_id,tp):
    pdf = PDFGen()
    #
    root = pdf.new_object({
        PDFGen.PDFName("Type"): PDFGen.PDFName("Catalog"),
        PDFGen.PDFName("Lang"): "en-US"
    })
    page1 = pdf.new_object({
        PDFGen.PDFName("Type"): PDFGen.PDFName("Page")
    })
    pages = pdf.new_object({
        PDFGen.PDFName("Type"): PDFGen.PDFName("Pages"),
        PDFGen.PDFName("Count"): 1,
        PDFGen.PDFName("Kids"): [ PDFGen.PDFIndirect(page1.id) ]
    })
    root.value[PDFGen.PDFName("Pages")] = PDFGen.PDFIndirect(pages.id)
    #
    f = open(path,"w",encoding="UTF-8")
    pdf.write_file(f)
    f.close()

os.system("rm -Rf reference/text/tables; mkdir -p reference/text/tables")
os.system("rm -Rf reference/html/tables; mkdir -p reference/html/tables")
os.system("rm -Rf reference/pdf/tables; mkdir -p reference/pdf/tables")

tables_json = common_json_help_module.load_json("compiled/tables.json")

tables = tables_json.get("tables")
if not tables == None:
    for table_id in tables:
        tp = table_presentation_module.TablePresentation(tables[table_id])
        emit_table_as_text("reference/text/tables/"+table_id+".txt",table_id,tp)
        emit_table_as_html("reference/html/tables/"+table_id+".htm",table_id,tp)
        emit_table_as_pdf("reference/pdf/tables/"+table_id+".pdf",table_id,tp)

