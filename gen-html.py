#!/usr/bin/python3

import os
import re
import glob
import json
import zlib
import math
import copy
import struct
import pathlib

import apodtoc
import apodjson
import apodhtml

sources = { }
def sources_load(sources,source_id):
    if not source_id in sources:
        sources[source_id] = apodjson.load_json("compiled/sources/"+source_id+".json")
    if source_id in sources:
        return sources[source_id]
    return None

class htmlelem:
    tag = None # string
    attr = None # object (dict) key=string, value=string
    content = None # binary
    def __init__(self,tag,attr={ },content=None):
        self.content = self.encodecontent(content)
        self.attr = attr
        self.tag = tag
    def encodecontent(self,content):
        if isinstance(content,list):
            r = b""
            for cent in content:
                r += self.encodecontent(cent)
            return r
        else:
            if not content == None and isinstance(content,str):
                return apodhtml.htmlescape(content).encode('UTF-8')
            elif isinstance(content,htmlelem): # we allow tags within tags here
                return content.gettag()
            else:
                return content
    def opentag(self):
        return b"<"+self.tagcontent()+b">"
    def closetag(self):
        return b"</"+self.tag.encode('UTF-8')+b">"
    def octag(self):
        return b"<"+self.tagcontent()+b" />"
    def tagcontent(self):
        r = self.tag.encode('UTF-8')
        if not self.attr == None and type(self.attr) == dict and len(self.attr) > 0:
            for key in self.attr:
                val = self.attr[key]
                r += b" "+key.encode('UTF-8')
                if not val == None:
                    r += b"=\""+apodhtml.htmlescape(val).encode('UTF-8')+b"\""
        return r
    def gettag(self):
        if not self.content == None:
            r = self.opentag()
            if not self.content == None:
                r += self.content
            r += self.closetag()
            return r
        else:
            return self.octag()

class htmlwriter:
    content = None
    stack = None
    def __init__(self):
        self.content = None
        self.stack = [ ]
    def out(self,x):
        if self.content == None:
            self.content = b""
        self.content += x
    def topelemopen(self):
        if len(self.stack) > 0 and self.stack[-1].content == None:
            self.stack[-1].content = b""
            self.out(self.stack[-1].opentag())
    def topelemclose(self):
        if len(self.stack) > 0:
            if self.stack[-1].content == None:
                self.out(self.stack[-1].octag())
            else:
                self.out(self.stack[-1].closetag())
    def write(self,whtmlelem):
        self.topelemopen()
        self.out(whtmlelem.gettag())
    def get(self):
        if len(self.stack) > 0:
            raise Exception("Attempt to render HTML without closing all tags with end()")
        if not self.content == None:
            r = self.content
        else:
            r = b""
        self.content = None
        return r
    def begin(self,htmlelem):
        self.topelemopen()
        self.stack.append(htmlelem)
    def end(self):
        if len(self.stack) == 0:
            raise Exception("HTML end with nothing left")
        self.topelemclose()
        self.stack.pop()

def genfrag_sinfo_row(hw,name,value,rowattr={}):
    hw.begin(htmlelem(tag="tr",attr=rowattr))
    hw.write(htmlelem(tag="td",content=name))
    hw.write(htmlelem(tag="td",content=value))
    hw.end() # tr

def genfrag_sourceinfo(bookid,ji):
    hw = htmlwriter()
    hw.write(htmlelem(tag="a",attr={ "id": apodhtml.mkhtmlid("source",bookid) }))
    hw.begin(htmlelem(tag="table",attr={ "class": "apodsource" }))
    #
    genfrag_sinfo_row(hw,"ID:",bookid,rowattr={ "class": "apodsourceid" })
    if "type" in ji:
        genfrag_sinfo_row(hw,"Type:",ji["type"],rowattr={ "class": "apodsourcetype" })
    if "title" in ji:
        genfrag_sinfo_row(hw,"Title:",ji["title"],rowattr={ "class": "apodsourcetitle" })
    if "url" in ji:
        ahref = htmlelem(tag="a",content=ji["url"],attr={ "target": "_blank", "href": ji["url"] })
        genfrag_sinfo_row(hw,"URL:",ahref,rowattr={ "class": "apodsourceurl" })
    if "author" in ji:
        genfrag_sinfo_row(hw,"Author:",ji["author"],rowattr={ "class": "apodsourceauthor" })
    if "publisher" in ji:
        genfrag_sinfo_row(hw,"Publisher:",ji["publisher"],rowattr={ "class": "apodsourcepublisher" })
    if "language" in ji:
        genfrag_sinfo_row(hw,"Language:",ji["language"],rowattr={ "class": "apodsourcelanguage" })
    if "copyright" in ji:
        cpy = ji["copyright"]
        r = "©"
        if "year" in cpy:
            r += " "+str(cpy["year"]);
        if "by" in cpy:
            r += " "+cpy["by"];
        genfrag_sinfo_row(hw,"Copyright:",r,rowattr={ "class": "apodsourcecopyright" })
    if "isbn" in ji:
        isbn = ji["isbn"]
        for what in isbn:
            genfrag_sinfo_row(hw,"ISBN:",isbn[what]+" ("+what.upper()+")",rowattr={ "class": "apodsourceisbn" })
    #
    hw.end() # table
    return hw.get()

def genfrag_sourcetoc(bookid,ji):
    if "table of contents" in ji:
        toc = ji["table of contents"]
        if "toc list" in toc:
            toclist = toc["toc list"]
            hw = htmlwriter()
            curlev = 0
            for tlent in toclist:
                if "path" in tlent and "title" in tlent and "depth" in tlent:
                    tlepth = tlent["path"]
                    tletit = tlent["title"]
                    tldpth = tlent["depth"]
                    lookup = apodtoc.apodsourcetocpathlookup(ji,tlepth)
                    if tldpth > (curlev+1):
                        raise Exception("Unexpected jump in depth")
                    if curlev < tldpth:
                        hw.begin(htmlelem(tag='ul',attr={ "class": "apodsourcetoclist" }))
                        curlev = curlev + 1
                    else:
                        while curlev > tldpth:
                            hw.end() # ul
                            curlev = curlev - 1
                    if not curlev == tldpth:
                        raise Exception("Depth mismatch")
                    c = [ htmlelem(tag='span',attr={ "class": "apodsourcetoclistenttitle" },content=tletit) ]
                    if not lookup == None:
                        if "page" in lookup:
                            c.append(" ")
                            c.append(htmlelem(tag='span',attr={ "class": "apodsourcetoclistentpagenumber" },content=("(page "+str(lookup["page"])+")")))
                    hw.write(htmlelem(tag='li',attr={ "class": "apodsourcetoclistent", "id": apodhtml.mkhtmlid("source",bookid,tlepth) },content=c))
            #
            while curlev > 0:
                hw.end() # ul
                curlev = curlev - 1
            #
            return hw.get()
    #
    return None

def genfrag_source(bookid,ji):
    r = genfrag_sourceinfo(bookid,ji)+b"\n"
    #
    tr = genfrag_sourcetoc(bookid,ji)
    if not tr == None and not tr == b"":
        r += tr+b"\n"
    #
    return r

def writefrag_source(bookid,ji,htmlfrag):
    path = "compiled/sources/"+bookid+".html.frag"
    f = open(path,"wb")
    f.write(htmlfrag)
    f.close()

def tablecolfloattohtml(tcolo,dcolo):
    if type(dcolo) == list:
        return str(dcolo)
    return str(dcolo)

def tablecolinttohtml(tcolo,dcolo):
    if type(dcolo) == list:
        return str(dcolo)
    if "display" in tcolo and tcolo["display"] == "hex":
        return hex(dcolo)
    return str(dcolo)

def tablecolbooltohtml(tcolo,dcolo):
    if dcolo == True:
        return "✓"
    else:
        return ""

# dcon = array of elements to write
# tcolo = column table info
# dcolo = column
def tablecoltohtml(dcon,tcolo,dcolo):
    if isinstance(dcolo,str):
        dcon.append(dcolo)
    elif "is array" in tcolo and tcolo["is array"] == True:
        if not type(dcolo) == list:
            raise Exception("array column not array")
        # each array of the element is an array containing a single value,
        # or two values to signify a range. perhaps the two value array should
        # just be an object that says "I'm a range"
        entc = 0
        for ent in dcolo:
            if entc > 0:
                dcon.append(", ")
            if isinstance(ent,str):
                dcon.append(ent)
            elif isinstance(ent,int):
                dcon.append(tablecolinttohtml(tcolo,ent))
            elif isinstance(ent,float):
                dcon.append(tablecolfloattohtml(tcolo,ent))
            elif not type(ent) == list:
                print(ent)
                raise Exception("array ent not an array")
            elif len(ent) == 1:
                dcon.append(htmlelem(tag="span",content=tablecolinttohtml(tcolo,ent[0])))
            elif len(ent) == 2:
                dcon.append(htmlelem(tag="span",content=(tablecolinttohtml(tcolo,ent[0])+"-"+tablecolinttohtml(tcolo,ent[1]))))
            else:
                print(ent)
                raise Exception("array ent is array with wrong number of elements")
            entc = entc + 1
    elif tcolo["type"] == "bool":
        if isinstance(dcolo,bool):
            dcon.append(tablecolbooltohtml(tcolo,dcolo==True))
        elif isinstance(dcolo,int):
            dcon.append(tablecolbooltohtml(tcolo,dcolo>0))
        else:
            print(dcolo)
            raise Exception("unexpected data type for bool")
    elif tcolo["type"] == "uint8_t" or tcolo["type"] == "uint_t":
        dcon.append(tablecolinttohtml(tcolo,dcolo))
    elif tcolo["type"] == "float":
        dcon.append(tablecolfloattohtml(tcolo,dcolo))

def genfrag_table(bookid,ji):
    hw = htmlwriter()
    hw.write(htmlelem(tag="a",attr={ "id": apodhtml.mkhtmlid("table",bookid) }))
    hw.write(htmlelem(tag="div",attr={ "class": "apodtitle", "title": bookid },content=ji["table"]))
    if "description" in ji:
        hw.write(htmlelem(tag="div",attr={ "class": "apoddescription" },content=ji["description"]))
    if "table columns" in ji and "rows" in ji:
        hw.begin(htmlelem(tag="table",attr={ "class": "apodtable" }))
        # header
        hw.begin(htmlelem(tag="tr",attr={ "class": "apodtablehead" }))
        for colo in ji["table columns"]:
            title = ""
            if "title" in colo:
                title = colo["title"]
            hw.write(htmlelem(tag="th",content=title))
        hw.end() # th
        # rows
        for rowo in ji["rows"]:
            if not "data" in rowo:
                continue
            hw.begin(htmlelem(tag="tr",attr={ "class": "apodtablerow" }))
            for coli in range(0,len(rowo["data"])):
                tcolo = ji["table columns"][coli]
                dcolo = rowo["data"][coli]
                dcon = [ ]
                if type(dcolo) == dict:
                    if "type" in dcolo and dcolo["type"] == "multiple" and "values" in dcolo and type(dcolo["values"]) == list:
                        for val in dcolo["values"]:
                            if "value" in val:
                                sdcon = [ ]
                                tablecoltohtml(sdcon,tcolo,val["value"])
                                dcon.append(htmlelem(tag="div",content=sdcon))
                else:
                    tablecoltohtml(dcon,tcolo,dcolo)
                hw.write(htmlelem(tag="td",content=dcon))
            hw.end() # tr
        # end
        hw.end() # table
    if "notes" in ji:
        nl = ji["notes"]
        if not type(nl) == list:
            nl = [ nl ]
        uli = [ ]
        for nent in nl:
            uli.append(htmlelem(tag="li",content=nent))
        nc = [ htmlelem(tag="span",attr={ "class": "apodnoteshead" },content="Notes:"), htmlelem(tag="ul",attr={ "class": "apodnoteslist" },content=uli) ]
        hw.write(htmlelem(tag="div",attr={ "class": "apodnotes", "title": bookid },content=nc))
    if "sources" in ji:
        uli = [ ]
        sl = ji["sources"]
        if not type(sl) == list:
            raise Exception("sources list not an array")
        for sil in range(0,len(sl)):
            nent = [ ]
            sel = sl[sil]
            if not type(sel) == dict:
                raise Exception("source element not object")
            if not "id" in sel:
                raise Exception("source has no id?")
            if not "source index" in sel:
                raise Exception("source object without source index")
            if not sel["source index"] == sil:
                raise Exception("source object wrong source index")
            if not "source" in sel:
                continue
            src = sel["source"]
            if not type(src) == dict:
                raise Exception("source element source not object")
            if not "id" in src:
                continue
            sref = sources_load(sources,src["id"])
            if sref == None:
                raise Exception("No such source "+src["id"])
            title = src["id"]
            if "title" in sref:
                title = sref["title"]
            if "title" in src:
                title = src["title"]
            copyright = ""
            if "copyright" in sref:
                cpy = sref["copyright"]
                if "year" in cpy:
                    if not copyright == "":
                        copyright += ", "
                    copyright += str(cpy["year"])
                if "by" in cpy:
                    if not copyright == "":
                        copyright += ", "
                    copyright += cpy["by"]
            #
            l = title
            if not copyright == "":
                l += ", "
                l += copyright
            nent.append(l)
            #
            url = None
            if "url" in sref:
                url = sref["url"]
            if "url" in src:
                url = src["url"]
            if not url == None and not url == "":
                nent.append(htmlelem(tag="br"))
                nent.append(htmlelem(tag="a",attr={ "class": "apodsourceurl", "target": "_blank", "href": url },content=apodhtml.unescapeurl(url)))
            #
            where = None
            if "where" in src:
                where = src["where"]
            if not where == None and type(where) == dict:
                if "path" in where and type(where["path"]) == list:
                    path = where["path"]
                    pref = apodtoc.apodsourcetocpathlookup(sref,path)
                    if not pref == None:
                        l = [ ]
                        if "title" in pref:
                            if not len(l) == 0:
                                l.append(", ")
                            l.append(htmlelem(tag="span",content='"'))
                            l.append(htmlelem(tag="span",attr={ "class": "apodsourcepreftitle" },content=pref["title"]))
                            l.append(htmlelem(tag="span",content='"'))
                        if "page" in pref:
                            if not len(l) == 0:
                                l.append(", ")
                            l.append(htmlelem(tag="span",attr={ "class": "apodsourceprefpage" },content=("(page "+str(pref["page"])+")")))
                    if not l == None:
                        nent.append(htmlelem(tag="br"))
                        nent.append(htmlelem(tag="div",attr={ "class": "apodsourcepref" },content=l))
            #
            uli.append(htmlelem(tag="li",content=nent))
        #
        nc = [ htmlelem(tag="span",attr={ "class": "apodsourceshead" },content="Sources:"), htmlelem(tag="ul",attr={ "class": "apodsourceslist" },content=uli) ]
        hw.write(htmlelem(tag="div",attr={ "class": "apodsources", "title": bookid },content=nc))
    r = hw.get()
    return r

def writefrag_table(bookid,ji,htmlfrag):
    path = "compiled/tables/"+bookid+".html.frag"
    f = open(path,"wb")
    f.write(htmlfrag)
    f.close()

def writewhole_beginhead(f):
    f.write("<!DOCTYPE HTML>\n<html><head>".encode('UTF-8'))
    f.write("<meta charset=\"UTF-8\" />".encode('UTF-8'))
    f.write("<meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\" />".encode('UTF-8'))

def writewhole_endhead(f):
    f.write(b"</head>\n")

def writewhole_beginbody(f):
    f.write("<body>\n".encode('UTF-8'))

def writewhole_endbody(f):
    f.write("</body></html>".encode('UTF-8'))

def writewhole_source(bookid,ji,htmlfrag):
    path = "compiled/sources/"+bookid+".html"
    f = open(path,"wb")
    writewhole_beginhead(f)
    if "title" in ji:
        f.write(("<title>"+apodhtml.htmlescape(ji["title"])+"</title>").encode('UTF-8'))
    f.write(("<link rel=\"stylesheet\" href=\"../sources.css\" />").encode('UTF-8'))
    writewhole_endhead(f)
    writewhole_beginbody(f)
    f.write(htmlfrag)
    writewhole_endbody(f)
    f.close()

def writewhole_table(bookid,ji,htmlfrag):
    path = "compiled/tables/"+bookid+".html"
    f = open(path,"wb")
    writewhole_beginhead(f)
    if "title" in ji:
        f.write(("<title>"+apodhtml.htmlescape(ji["title"])+"</title>").encode('UTF-8'))
    f.write(("<link rel=\"stylesheet\" href=\"../tables.css\" />").encode('UTF-8'))
    writewhole_endhead(f)
    writewhole_beginbody(f)
    f.write(htmlfrag)
    writewhole_endbody(f)
    f.close()

def englishpp(x):
    if x[0:4].lower() == "the ":
        x = x[4:]+", "+x[0:4]
    return x

def tableprocsort(x):
    return [ x["title"].lower(), x["id"] ]

def sourceprocsort(x):
    return [ x["title"].lower(), x["id"] ]

# process
sourceproclist = [ ]
g = glob.glob("compiled/sources/*.json",recursive=True)
for path in g:
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    #
    ji = apodjson.load_json(path)
    if not "id" in ji:
        continue
    if not "type" in ji:
        continue
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename == (ji["id"] + ".json"):
        raise Exception("Book "+ji["id"]+" id does not match filename "+basename)
    #
    htmlfrag = genfrag_source(ji["id"],ji)
    writefrag_source(ji["id"],ji,htmlfrag)
    writewhole_source(ji["id"],ji,htmlfrag)
    #
    title = ji["id"]
    if "title" in ji:
        title = englishpp(ji["title"])
    sourceproclist.append({ "id": ji["id"], "title": title })
#
sourceproclist.sort(key=sourceprocsort)

# process
tableproclist = [ ]
g = glob.glob("compiled/tables/*.json",recursive=True)
for path in g:
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    #
    ji = apodjson.load_json(path)
    if not "id" in ji:
        continue
    #
    htmlfrag = genfrag_table(ji["id"],ji)
    writefrag_table(ji["id"],ji,htmlfrag)
    writewhole_table(ji["id"],ji,htmlfrag)
    #
    title = ji["id"]
    if "table" in ji:
        title = englishpp(ji["table"])
    tableproclist.append({ "id": ji["id"], "title": title })
#
tableproclist.sort(key=tableprocsort)

# make overall source list HTML too
f = open("compiled/sources.html","wb")
writewhole_beginhead(f)
f.write("<title>Sources</title>".encode('UTF-8'))
f.write(("<link rel=\"stylesheet\" href=\"sources.css\" />").encode('UTF-8'))
writewhole_endhead(f)
writewhole_beginbody(f)
#
for sobj in sourceproclist:
    hw = htmlwriter()
    le = [ "Source ", htmlelem(tag="a",attr={ "href": "#"+apodhtml.mkhtmlid("source",sobj["id"]), "title": sobj["id"], "class": "apodsourceslisttitle" },content=sobj["title"]) ]
    hw.write(htmlelem(tag="div",attr={ "class": "apodsourceslistent" },content=le))
    f.write(hw.get())
f.write(b"<hr class=\"apodsourcetoclistentseparator\" />\n")
#
sidcount = 0
for sobj in sourceproclist:
    sid = sobj["id"]
    if sidcount > 0:
        f.write(b"<hr class=\"apodsourcetoclistentseparator\" />\n")
    path = "compiled/sources/"+sid+".html.frag"
    sf = open(path,"rb")
    f.write(sf.read())
    sf.close()
    sidcount = sidcount + 1
    os.unlink(path) # don't leave them around!
writewhole_endbody(f)
f.close()

# make overall table list HTML too
f = open("compiled/tables.html","wb")
writewhole_beginhead(f)
f.write("<title>Tables</title>".encode('UTF-8'))
f.write(("<link rel=\"stylesheet\" href=\"tables.css\" />").encode('UTF-8'))
writewhole_endhead(f)
writewhole_beginbody(f)
#
for sobj in tableproclist:
    hw = htmlwriter()
    le = [ "Table ", htmlelem(tag="a",attr={ "href": "#"+apodhtml.mkhtmlid("table",sobj["id"]), "title": sobj["id"], "class": "apodtableslisttitle" },content=sobj["title"]) ]
    hw.write(htmlelem(tag="div",attr={ "class": "apodtableslistent" },content=le))
    f.write(hw.get())
f.write(b"<hr class=\"apodtabletoclistentseparator\" />\n")
#
sidcount = 0
for sobj in tableproclist:
    sid = sobj["id"]
    if sidcount > 0:
        f.write(b"<hr class=\"apodtableseparator\" />\n")
    path = "compiled/tables/"+sid+".html.frag"
    sf = open(path,"rb")
    f.write(sf.read())
    sf.close()
    sidcount = sidcount + 1
    os.unlink(path) # don't leave them around!
writewhole_endbody(f)
f.close()

# cascading stylesheet too
sf = open("sources.html.css","rb")
df = open("compiled/sources.css","wb")
df.write(sf.read())
df.close()
sf.close()
# cascading stylesheet too
sf = open("tables.html.css","rb")
df = open("compiled/tables.css","wb")
df.write(sf.read())
df.close()
sf.close()
