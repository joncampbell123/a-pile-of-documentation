
# TODO: Someday, figure out the bloody fucking magic ritual incantations that one has to do to get PDF files to carry Unicode text,
#       because I've tried everything and nothing works. We're stuck in plain ASCII for now. >:( --J.C.

import os
import glob
import json
import zlib
import struct
import pathlib

import ttf_module
import pdf_module
import html_module
import common_json_help_module

import freetype # some things are super complicated and are better left to the professionals (pip3 install freetype-py)

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
    zlib_compress_streams = None
    #
    def __init__(self,optobj=None):
        self.root_id = None
        self.pdfver = [ 1, 4 ]
        self.objects = [ None ] # object 0 is always NULL because most PDFs seem to count from 1
        self.zlib_compress_streams = False
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
                if self.zlib_compress_streams == True and len(obj.data) > 0:
                    cmp = zlib.compressobj(level=9,method=zlib.DEFLATED,wbits=15,memLevel=9)
                    z = cmp.compress(obj.data)
                    z += cmp.flush(zlib.Z_FINISH)
                    if len(obj.data) > len(z):
                        obj.header.value[PDFName("Filter")] = PDFName("FlateDecode")
                        obj.data = z
                    del cmp
                #
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
                ttf = ttf_module.TTFFile(ttfdata)
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
                    fontpdfobj.value[PDFName("FirstChar")] = pdfinfo.firstChar
                if not pdfinfo.lastChar == None:
                    fontpdfobj.value[PDFName("LastChar")] = pdfinfo.lastChar
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
                # now the complicated part: reading glyph widths, and mapping chars to glyphs, to build the Width table.
                # Not only does PDF expect /Widths but it will also help the PDF export know how to lay out text properly.
                ft = freetype.Face(ttffile)
                char2glyph = ft.get_chars() # pair (uchar,glyph)
                ft.set_char_size(1) # NTS: Not sure why this makes proper spacing with linearHoriAdvance?
                widths = [ ]
                while len(widths) < (pdfinfo.lastChar + 1 - pdfinfo.firstChar):
                    widths.append(0)
                for [char,glyphidx] in char2glyph:
                    if char >= pdfinfo.firstChar and char <= pdfinfo.lastChar:
                        widx = char - pdfinfo.firstChar
                        ft.load_glyph(glyphidx)
                        widths[widx] = int(ft.glyph.linearHoriAdvance / 65.536)
                #
                fontdict[PDFName("Widths")] = widths
                del ft
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
    def fontwidth(self,font,size,text):
        sz = 0
        fc = font.value.get(PDFName("FirstChar"))
        if fc == None:
            fc = 0
        fw = font.value.get(PDFName("Widths"))
        if not fw == None:
            for c in text:
                ci = ord(c) - fc
                if ci >= 0 and ci < len(fw):
                    sz = sz + (fw[ci] * size) / 1000.0
        #
        return sz / self.page_dpi

class PDFPageContentWriter:
    wd = None
    intxt = None
    pdfhl = None
    currentFont = None
    currentFontSize = None
    def data(self):
        return self.wd
    def __init__(self,pdfhl):
        self.wd = bytes()
        self.intxt = False
        self.pdfhl = pdfhl
        self.currentFont = None
        self.currentFontSize = None
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
    def text_width(self,text):
        if self.currentFont == None or self.currentFontSize == None:
            raise Exception("No current font")
        return self.pdfhl.fontwidth(self.currentFont,self.currentFontSize,text)
    def set_text_font(self,font_id,size):
        if not self.intxt == True:
            raise Exception("Not in text")
        self.currentFont = font_id
        self.currentFontSize = size
        if not type(font_id) == PDFObject:
            raise Exception("set_text_font must specify font object")
        if not PDFName("Name") in font_id.value:
            raise Exception("PDFObject as font id with no Name")
        font_id = font_id.value[PDFName("Name")]
        if not type(font_id) == PDFName:
            raise Exception("PDFObject as font id with value that is not PDFName")
        font_id = font_id.name
        if not type(font_id) == str:
            raise Exception("PDFObject as font id with value that is PDFName not a str")
        #
        if font_id[0] == 'F':
            font_id = font_id[1:]
        #
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

