#!/usr/bin/python3

import os
import glob
import json
import struct
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

def pdf_str_escape(v):
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
    return r;

# the world's simplest PDF generator class
class PDFName:
    name = None
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return self.name
    def __eq__(self,other):
        if other == None:
            return False
        return self.name.__eq__(other.name)
    def __hash__(self):
        return self.name.__hash__()

class PDFIndirect:
    id = None
    def __init__(self,id):
        if type(id) == PDFObject or type(id) == PDFStream:
            id = id.id
        elif not type(id) == int:
            raise Exception("PDFIndirect id must be integer")
        self.id = id

class PDFStream:
    id = None
    data = None
    header = None
    def __init__(self,data):
        self.header = PDFObject({})
        self.data = data

class PDFObject:
    id = None
    index = None
    value = None
    type = None # boolean, integer, real, text string, hex string, name, array, dict, stream, null, indirect
    def __init__(self,value=None,*,vtype=None):
        self.type = None
        self.set(value,vtype=vtype)
    def setkey(self,key,value):
        if type(self.value) == dict:
            self.value[key] = value
        else:
            raise Exception("Data type does not accept key value mapping ("+str(type(self.value)))
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
            elif type(value) == PDFName:
                vtype = PDFName
            elif type(value) == list:
                vtype = list
            elif type(value) == dict:
                vtype = dict
            elif type(value) == PDFStream:
                vtype = PDFStream
            elif value == None:
                vtype = None
            elif type(value) == PDFIndirect:
                vtype = PDFIndirect
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
        elif vtype == PDFName:
            if type(value) == str:
                self.value = PDFName(value)
            elif type(value) == PDFName:
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
        elif vtype == PDFStream:
            if type(value) == bytes:
                self.value = PDFStream(value)
            elif type(value) == PDFStream:
                self.value = value
            else:
                raise Exception("PDFStream must be PDFStream")
        elif vtype == None:
            if value == None:
                self.value = value
            else:
                raise Exception("None must be none")
        elif vtype == PDFIndirect:
            if type(value) == int:
                self.value = PDFIndirect(value)
            elif type(value) == PDFIndirect:
                self.value = value
            elif type(value) == PDFObject:
                self.value = value.id
            else:
                raise Exception("PDFIndirect must be PDFIndirect")
        else:
            raise Exception("Don't know how to handle type "+str(vtype)+" value "+str(value))

class PDFGen:
    pdfver = None
    objects = None
    root_id = None
    #
    def __init__(self,optobj=None):
        self.root_id = None
        self.pdfver = [ 1, 4 ]
        self.objects = [ None ] # object 0 is always NULL because most PDFs seem to count from 1
    #
    def new_stream_object(self,value=None):
        id = len(self.objects)
        obj = PDFStream(value)
        self.objects.append(obj)
        obj.id = id
        return obj
    def new_object(self,value=None,*,vtype=None):
        id = len(self.objects)
        obj = PDFObject(value,vtype=vtype)
        self.objects.append(obj)
        obj.id = id
        return obj
    def set_root_object(self,obj):
        if type(obj) == int:
            self.root_id = obj
        elif type(obj) == PDFObject:
            self.root_id = obj.id
        else:
            raise Exception("Set root node given invalid object")
    #
    def serialize(self,obj):
        if not type(obj) == PDFObject:
            obj = PDFObject(obj)
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
            return "("+pdf_str_escape(obj.value)+")"
        elif obj.type == bytes:
            r = ""
            for c in obj.value:
                h = hex(c)[2:].upper() # strip off 0x, also Adobe says it can be upper or lower case, I choose upper
                if len(h) < 2:
                    h = '0'+h
                r = r + h
            return "<"+r+">"
        elif obj.type == PDFName:
            return "/" + str(obj.value.name)
        elif obj.type == list:
            r = ""
            for ent in obj.value:
                if not r == "":
                    r = r + " "
                r = r + self.serialize(ent)
            return "["+r+"]"
        elif obj.type == dict:
            r = ""
            for key in obj.value:
                objval = obj.value[key]
                if not type(key) == PDFName:
                    raise Exception("dict keys must be PDFName not "+type(key))
                if type(key) == PDFName and (type(objval) == PDFName or type(objval) == str or type(objval) == bytes or type(objval) == list or type(objval) == PDFObject):
                    r = r + self.serialize(key) + self.serialize(objval)
                else:
                    r = r + self.serialize(key) + " " + self.serialize(objval)
            return "<<"+r+">>"
        elif obj.type == PDFStream:
            raise Exception("PDFStream serialize directly")
        elif obj.type == None:
            return "null"
        elif obj.type == PDFIndirect:
            return str(obj.value.id)+" 0 R"
        else:
            raise Exception("Unknown type on serialize")
    #
    def write_file(self,f):
        objofs = [ ]

        if self.root_id == None:
            raise Exception("PDFGen root node not specified")
        if self.root_id < 0 or self.root_id >= len(self.objects):
            raise Exception("PDFGen root node out of range")

        f.seek(0)
        f.write(("%PDF-"+str(self.pdfver[0])+"."+str(self.pdfver[1])+"\n").encode())
        f.write("%".encode()+bytes([0xC2,0xB5,0xC2,0xB6])+"\n\n".encode()) # non-ASCII chars to convince other programs this is not text
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
            #
            if len(objofs) == objid:
                objofs.append(f.tell())
            else:
                raise Exception("objid count error")
            #
            f.write((str(objid)+" 0 obj\n").encode())
            if type(obj) == PDFObject:
                f.write(self.serialize(obj).encode())
            elif type(obj) == PDFStream:
                obj.header.value[PDFName("Length")] = len(obj.data)
                f.write(self.serialize(obj.header).encode())
                f.write("\n".encode())
                f.write("stream\n".encode())
                f.write(obj.data)
                f.write("\n".encode())
                f.write("endstream".encode())
            else:
                raise Exception("unsupported object")
            #
            f.write("\n".encode())
            f.write("endobj\n\n".encode())
        #
        xrefofs = f.tell()
        f.write("xref\n".encode())
        f.write(("0 "+str(len(self.objects))+"\n").encode())
        # NTS: Each xref entry must be 20 bytes each
        for objid in range(len(self.objects)):
            ofs = objofs[objid]
            if not ofs == None:
                s = str(ofs)[0:10]
                if len(s) < 10:
                    s = ("0"*(10-len(s)))+s
                f.write((s+" 00000 n \n").encode())
            else:
                f.write(("0000000000 00000 f \n").encode())
        f.write("\n".encode())
        #
        f.write("trailer\n".encode())
        f.write(self.serialize({
            PDFName("Size"): len(self.objects),
            PDFName("Root"): PDFIndirect(self.root_id)
        }).encode())
        f.write("\n".encode())
        #
        f.write("startxref\n".encode())
        f.write((str(xrefofs)+"\n").encode())
        f.write("%%EOF\n".encode())

class TTFFileTable:
    tag = None
    offset = None
    length = None
    checksum = None
    data = None
    def __init__(self,tag,checksum,offset,length):
        self.tag = tag
        self.checksum = checksum
        self.offset = offset
        self.length = length
    def __str__(self):
        return "{ tag="+self.tag.decode()+" chk="+hex(self.checksum)+" offset="+str(self.offset)+" size="+str(self.length)+" }"

class TTFInfoForPDF:
    Ascent = None
    Descent = None
    isFixedPitch = None
    fontWeight = None
    italicAngle = None
    unitsPerEm = None
    firstChar = None
    lastChar = None
    xMin = None
    yMin = None
    xMax = None
    yMax = None

class TTFFile:
    tables = None
    version = None
    def __init__(self,data):
        [self.version,numTables,searchRange,entrySelector,rangeShift] = struct.unpack(">LHHHH",data[0:12])
        self.tables = [ ]
        for ti in range(numTables):
            ofs = 12+(ti*16)
            #
            tag = data[ofs:ofs+4]
            [checkSum,offset,length] = struct.unpack(">LLL",data[ofs+4:ofs+16])
            #
            te = TTFFileTable(tag,checkSum,offset,length)
            te.data = data[offset:offset+length]
            #
            self.tables.append(te)
    def lookup(self,id):
        for ti in self.tables:
            if ti.tag.decode().strip() == id:
                return ti
        return None
    def get_info_for_pdf(self):
        r = TTFInfoForPDF()
        #
        post = self.lookup("post")
        if not post == None:
            # FIXED: 32-bit fixed pt (L)
            # FWORD: 16-bit signed int (h)
            # ULONG: 32-bit unsigned long (L)
            [FormatType,r.italicAngle,underlinePosition,underlineThickness,r.isFixedPitch] = struct.unpack(">LLhhL",post.data[0:16])
            del post
        #
        head = self.lookup("head")
        if not head == None:
            # FIXED: 32-bit fixed pt (L)
            # FWORD: 16-bit signed int (h)
            # USHORT: 16-bit unsigned int (H)
            # ULONG: 32-bit unsigned long (L)
            [tableversion,fontRevision,checkSumAdjustment,magicNumber,flags,r.unitsPerEm] = struct.unpack(">LLLLHH",head.data[0:20])
            # skip the two created/modified timestamps, each 8 bytes long
            [r.xMin,r.yMin,r.xMax,r.yMax] = struct.unpack(">hhhh",head.data[36:36+8])
            del head
        #
        os2 = self.lookup("OS/2")
        if not os2 == None:
            [version,xAvgCharWidth,r.fontWeight] = struct.unpack(">HhH",os2.data[0:6])
            [r.firstChar,r.lastChar] = struct.unpack(">HH",os2.data[64:64+4])
            del os2
        #
        hhea = self.lookup("hhea")
        if not hhea == None:
            [tableVersion,r.Ascent,r.Descent] = struct.unpack(">Lhh",hhea.data[0:8])
            del hhea
        #
        return r

class PDFGenHL:
    pdf = None
    root_node = None
    pages_node = None
    pages = None
    page_size = None
    page_dpi = None
    def __init__(self,pdf):
        self.pdf = pdf
        self.page_size = [ 8, 11 ]
        self.page_dpi = 72
        self.pages = [ None ] # count from 1, fill slot 0, array of PDFIndirect
        #
        self.root_node = self.pdf.new_object({
            PDFName("Type"): PDFName("Catalog"),
            PDFName("Lang"): "en-US"
        })
        self.pdf.set_root_object(self.root_node)
        #
        self.pages_node = self.pdf.new_object({
            PDFName("Type"): PDFName("Pages")
        })
        self.root_node.setkey(PDFName("Pages"), PDFIndirect(self.pages_node))
    def finish(self):
        self.pages_node.setkey(PDFName("Count"), len(self.pages) - 1) # slot 0 does not count
        self.pages_node.setkey(PDFName("Kids"), self.pages[1:])
    def new_page(self):
        pagedir = self.pdf.new_object({
            PDFName("Type"): PDFName("Page"),
            PDFName("Parent"): PDFIndirect(self.pages_node),
            PDFName("MediaBox"): [ 0, 0, self.page_size[0]*self.page_dpi, self.page_size[1]*self.page_dpi ]
        })
        pagedir.index = len(self.pages)
        pageindir = PDFIndirect(pagedir)
        self.pages.append(pageindir)
        return pagedir
    def get_page(self,page):
        po = self.pages[page]
        if po == None:
            return None
        return self.pdf.objects[po.id]
    def make_page_content_stream(self,pageobj,*,data=bytes()):
        if PDFName("Contents") in pageobj.value:
            return
        page_content = self.pdf.new_stream_object(data)
        pageobj.setkey(PDFName("Contents"), PDFIndirect(page_content))
    def add_page_font_ref(self,pageobj,info):
        if not PDFName("Resources") in pageobj.value:
            res_obj = PDFObject({})
            pageobj.setkey(PDFName("Resources"), res_obj)
            res_obj.setkey(PDFName("ProcSet"), [ PDFName("PDF"), PDFName("Text"), PDFName("ImageB"), PDFName("ImageC"), PDFName("ImageI") ])
        else:
            res_obj = pageobj.value[PDFName("Resources")]
        #
        fontname = info.value.get(PDFName("Name"))
        if fontname == None:
            raise Exception("Font without a name")
        #
        if not PDFName("Font") in res_obj.value:
            font_obj = PDFObject({})
            res_obj.setkey(PDFName("Font"), font_obj)
        else:
            font_obj = res_obj.value[PDFName("Font")]
        #
        if not PDFName(fontname) in font_obj.value:
            font_obj.setkey(PDFName(fontname), PDFIndirect(info))
        else:
            raise Exception("Font already added")
    def add_font(self,fontdict,*,desc=None,ttffile=None):
        fontdict[PDFName("Type")] = PDFName("Font")
        if not desc == None:
            fdo = {
                PDFName("Type"): PDFName("FontDescriptor")
            }
            #
            if PDFName("BaseFont") in fontdict:
                fdo[PDFName("FontName")] = fontdict[PDFName("BaseFont")]
            #
            fontpdfobj = self.pdf.new_object(fontdict)
            #
            if not ttffile == None:
                f = open(ttffile,"rb")
                ttfdata = f.read()
                ttf = TTFFile(ttfdata)
                f.close()
                pdfinfo = ttf.get_info_for_pdf()
                if not pdfinfo.italicAngle == None:
                    fdo[PDFName("ItalicAngle")] = pdfinfo.italicAngle
                if not pdfinfo.fontWeight == None:
                    fdo[PDFName("FontWeight")] = pdfinfo.fontWeight
                if not pdfinfo.xMin == None:
                    fdo[PDFName("FontBBox")] = [ pdfinfo.xMin, pdfinfo.yMin, pdfinfo.xMax, pdfinfo.yMax ]
                if not pdfinfo.Ascent == None:
                    fdo[PDFName("Ascent")] = pdfinfo.Ascent
                if not pdfinfo.Descent == None:
                    fdo[PDFName("Descent")] = pdfinfo.Descent
                if not pdfinfo.firstChar == None:
                    fdo[PDFName("FirstChar")] = pdfinfo.firstChar
                if not pdfinfo.lastChar == None:
                    fdo[PDFName("LastChar")] = pdfinfo.lastChar
                #
                # CAREFUL! Adobe documents LSB as bit 1 and MSB as bit 32
                #
                # bit 0: FixedPitch
                # bit 1: Serif
                # bit 2: Symbolic
                # bit 3: Script
                # bit 5: Nonsymbolic
                # bit 6: Italic
                # bit 16: AllCap
                flags = 0
                if pdfinfo.isFixedPitch:
                    flags = flags | (1 << 0)
                #
                fdo[PDFName("Flags")] = flags
                # I don't know how to get this from the TTF so just guess
                fdo[PDFName("StemV")] = 52
            #
            fontdict[PDFName("FontDescriptor")] = PDFIndirect(self.pdf.new_object(fdo))
            #
            if not ttffile == None:
                # finally, make a stream_object for the TTF file and point to it from the font descriptor
                fontstream = self.pdf.new_stream_object(ttfdata)
                # PDF stream objects always list their length as /Length
                # Except Font TTF streams, which require the same size specified as /Length1 (facepalm)
                fontstream.header.value[PDFName("Length1")] = len(ttfdata)
                fdo[PDFName("FontFile2")] = PDFIndirect(fontstream)
        #
        return fontpdfobj

class PDFPageContentWriter:
    wd = None
    intxt = None
    def data(self):
        return self.wd
    def __init__(self):
        self.wd = bytes()
        self.intxt = False
    def rstrip(self):
        i = len(self.wd) - 1
        while i >= 0 and self.wd[i:i+1] == b' ':
            i = i - 1
        i = i + 1
        if not len(self.wd) == i:
            self.wd = self.wd[0:i]
    def begin_text(self):
        if self.intxt == True:
            raise Exception("Already in text")
        self.intxt = True
        self.wd += "BT ".encode()
    def end_text(self):
        if not self.intxt == True:
            raise Exception("Not in text, cannot end")
        self.intxt = False
        self.wd += "ET ".encode()
    def set_text_font(self,font_id,size):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.rstrip()
        self.wd += ("/F"+str(font_id)+" "+str(size)+" Tf ").encode()
    def text_move_to(self,x,y):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.wd += (str(x)+" "+str(y)+" Td ").encode()
    def text(self,text):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.rstrip()
        self.wd += ("("+pdf_str_escape(text)+") Tj ").encode()
    def text_leading(self,l):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.wd += (str(l)+" TL ").encode()
    def text_next_line(self):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.wd += "T* ".encode()
    def fill_color(self,r,g,b):
        self.wd += (str(r)+" "+str(g)+" "+str(b)+" rg ").encode()
    def stroke_color(self,r,g,b):
        self.wd += (str(r)+" "+str(g)+" "+str(b)+" RG ").encode()
    def linewidth(self,l):
        self.wd += (str(l)+" w ").encode()
    def moveto(self,x,y):
        self.wd += (str(x)+" "+str(y)+" m ").encode()
    def lineto(self,x,y):
        self.wd += (str(x)+" "+str(y)+" l ").encode()
    def close_subpath(self):
        self.wd += ("h ").encode()
    def stroke(self):
        self.wd += ("S ").encode()
    def fill(self):
        self.wd += ("f ").encode()
    def stroke_and_fill(self):
        self.wd += ("B ").encode()
    def finish(self):
        if self.intxt == True:
            self.end_text()

def emit_table_as_pdf(path,table_id,tp):
    pdf = PDFGen()
    pdfhl = PDFGenHL(pdf)
    #
    font1 = pdfhl.add_font({
        PDFName("Subtype"): PDFName("TrueType"),
        PDFName("Name"): PDFName("F1"),
        PDFName("Encoding"): PDFName("WinAnsiEncoding"),
        PDFName("BaseFont"): PDFName("ABCDEE+Ubuntu")
    },
    desc={
    },
    ttffile="ttf/Ubuntu-R.ttf")
    #
    page1 = pdfhl.new_page()
    pdfhl.add_page_font_ref(page1,font1)
    page1cmd = PDFPageContentWriter()
    page1cmd.begin_text()
    page1cmd.text_leading(12)
    page1cmd.set_text_font(1,12)
    page1cmd.text_move_to(288,270)
    page1cmd.fill_color(0,0,0.5)
    page1cmd.text("Hello World. ")
    page1cmd.fill_color(0,0,1.0)
    page1cmd.text("This is a PDF")
    page1cmd.text_next_line()
    page1cmd.fill_color(1.0,0,0)
    page1cmd.text("1234ABCD")
    page1cmd.end_text()
    page1cmd.linewidth(2.0)
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.moveto(50,50)
    page1cmd.lineto(100,50)
    page1cmd.lineto(100,100)
    page1cmd.lineto(50,100)
    page1cmd.close_subpath()
    page1cmd.stroke()
    #
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.fill_color(0.5,0,0)
    page1cmd.moveto(150,50)
    page1cmd.lineto(200,50)
    page1cmd.lineto(200,100)
    page1cmd.lineto(150,100)
    page1cmd.close_subpath()
    page1cmd.fill()
    #
    page1cmd.stroke_color(0,0.5,0)
    page1cmd.fill_color(0.5,0,0)
    page1cmd.moveto(250,50)
    page1cmd.lineto(300,50)
    page1cmd.lineto(300,100)
    page1cmd.lineto(250,100)
    page1cmd.close_subpath()
    page1cmd.stroke_and_fill()
    #
    page1content = pdfhl.make_page_content_stream(page1,data=page1cmd.data())
    del page1cmd
    #
    page2 = pdfhl.new_page()
    #
    page2cmd = PDFPageContentWriter()
    page2cmd.begin_text()
    page2cmd.text_leading(12)
    page2cmd.set_text_font(1,12)
    page2cmd.text_move_to(288,270)
    page2cmd.fill_color(0,0,0.5)
    page2cmd.text("Page 2")
    page2cmd.end_text()
    page2cmd.linewidth(4.0)
    page2cmd.stroke_color(0,0.5,0)
    page2cmd.fill_color(0.5,0,0)
    page2cmd.moveto(250,50)
    page2cmd.lineto(300,50)
    page2cmd.lineto(300,100)
    page2cmd.lineto(250,100)
    page2cmd.close_subpath()
    page2cmd.stroke_and_fill()
    #
    page2content = pdfhl.make_page_content_stream(page2,data=page2cmd.data())
    del page2cmd
    #
    page1o = pdfhl.get_page(1)
    #
    pdfhl.finish()
    f = open(path,"wb")
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

