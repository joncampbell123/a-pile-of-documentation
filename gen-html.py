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

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")
if not os.path.exists("compiled/html"):
    os.mkdir("compiled/html")

sources = { }
def sources_load(sources,source_id):
    if not source_id in sources:
        sources[source_id] = apodjson.load_json("compiled/sources/"+source_id+".json")
    if source_id in sources:
        return sources[source_id]
    return None

def genfrag_sinfo_row(hw,name,value,rowattr={}):
    hw.begin(apodhtml.htmlelem(tag="tr",attr=rowattr))
    hw.write(apodhtml.htmlelem(tag="td",content=name))
    hw.write(apodhtml.htmlelem(tag="td",content=value))
    hw.end() # tr

def genfrag_sourceinfo(bookid,ji):
    hw = apodhtml.htmlwriter()
    hw.write(apodhtml.htmlelem(tag="a",attr={ "id": apodhtml.mkhtmlid("source",bookid) }))
    hw.begin(apodhtml.htmlelem(tag="table",attr={ "class": "apodsource" }))
    #
    genfrag_sinfo_row(hw,"ID:",bookid,rowattr={ "class": "apodsourceid" })
    if "type" in ji:
        genfrag_sinfo_row(hw,"Type:",ji["type"],rowattr={ "class": "apodsourcetype" })
    if "source json file" in ji:
        genfrag_sinfo_row(hw,"JSON:",ji["source json file"],rowattr={ "class": "apodsourcejsonfile" })
    if "title" in ji:
        genfrag_sinfo_row(hw,"Title:",ji["title"],rowattr={ "class": "apodsourcetitle" })
    if "url" in ji:
        ahref = apodhtml.htmlelem(tag="a",content=ji["url"],attr={ "target": "_blank", "href": ji["url"] })
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
            hw = apodhtml.htmlwriter()
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
                        hw.begin(apodhtml.htmlelem(tag='ul',attr={ "class": "apodsourcetoclist" }))
                        curlev = curlev + 1
                    else:
                        while curlev > tldpth:
                            hw.end() # ul
                            curlev = curlev - 1
                    if not curlev == tldpth:
                        raise Exception("Depth mismatch")
                    c = [ apodhtml.htmlelem(tag='span',attr={ "class": "apodsourcetoclistenttitle" },content=tletit) ]
                    if not lookup == None:
                        if "page" in lookup:
                            c.append(" ")
                            c.append(apodhtml.htmlelem(tag='span',attr={ "class": "apodsourcetoclistentpagenumber" },content=("(page "+str(lookup["page"])+")")))
                    hw.write(apodhtml.htmlelem(tag='li',attr={ "class": "apodsourcetoclistent", "id": apodhtml.mkhtmlid("source",bookid,tlepth) },content=c))
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

def tablecolfloattohtml(tcolo,dcolo):
    if type(dcolo) == list:
        return str(dcolo)
    return str(dcolo)

def hex8(x):
    x = hex(x)[2:].upper() # strip off the 0x
    while len(x) < 2:
        x = '0' + x
    return "0x"+x

def hexg(x):
    return "0x"+hex(x)[2:].upper() # strip off the 0x, uppercase, add it back

def tablecolinttohtml(tcolo,dcolo):
    if type(dcolo) == list:
        return str(dcolo)
    if "display" in tcolo and tcolo["display"] == "hex" and isinstance(dcolo,int):
        if tcolo["type"] == "uint8_t":
            return hex8(dcolo)
        return hexg(dcolo)
    return str(dcolo)

def tablecolbooltohtml(tcolo,dcolo):
    if dcolo == True:
        return "✓"
    else:
        return ""

def fmtstr(fmt,v):
    if fmt == "hex":
        return hex(v)
    elif fmt == "hex8":
        v = hex(v)[2:]
        while len(v) < 2:
            v = "0"+v
        return "0x"+v
    elif re.match(r'^bin\d+$',fmt):
        sz = int(fmt[3:])
        v = bin(v)[2:]
        while len(v) < sz:
            v = "0"+v
        return "0b"+v
    else:
        return str(v)

def tablecolenumtohtml(dcon,tcolo,ent,compiled_format):
    trs = [ ]
    columns = 1
    fields = { }
    if "fields" in ent:
        fields = ent["fields"]
    fmt = "dec"
    if "format" in ent:
        fmt = ent["format"]
    if "columns" in ent:
        columns = ent["columns"]
    col = 0
    row = 0
    enum = ent["enum"]
    enumcount = len(enum)
    #
    keyf = ""
    valf = ""
    if "keyname" in fields:
        keyf = fields["keyname"]
    if "valname" in fields:
        valf = fields["valname"]
    if not keyf == "" or not valf == "":
        tr = [ ]
        for cc in range(0,min(columns,enumcount)):
            tr.append(apodhtml.htmlelem(tag="th",content=keyf))
            tr.append(apodhtml.htmlelem(tag="th",content=valf))
        trs.append(apodhtml.htmlelem(tag="tr",attr={ "class": "apodenumtablerowhead" },content=tr))
    #
    for ent in enum:
        minv = ent["min"]
        maxv = ent["max"]
        #
        if col == 0:
            tr = [ ]
        #
        if minv == maxv:
            valstr = fmtstr(fmt,minv)
        else:
            valstr = fmtstr(fmt,minv)+" - "+fmtstr(fmt,maxv)
        tr.append(apodhtml.htmlelem(tag="td",attr={ "class": "apodenumtablecolidx" },content=valstr))
        #
        subdcon = [ ]
        tablecoltohtml(subdcon,tcolo,ent["value"],compiled_format)
        tr.append(apodhtml.htmlelem(tag="td",attr={ },content=subdcon))
        #
        col += 1
        if col >= columns:
            trs.append(apodhtml.htmlelem(tag="tr",attr={ "class": "apodenumtablerow" },content=tr))
            tr = [ ]
            row += 1
            col = 0
    #
    if col > 0:
        trs.append(apodhtml.htmlelem(tag="tr",attr={ "class": "apodenumtablerow" },content=tr))
    #
    dcon.append(apodhtml.htmlelem(tag="table",attr={ "class": "apodenumtable" },content=trs))

def tablecolbitfieldtohtml(dcon,tcolo,ent,compiled_format):
    colwidth = ent["colwidth"] # in em
    brange = ent["bitrange"]
    columns = brange["max"]+1-brange["min"]
    keycolumn = False
    #
    if "keyhead" in ent:
        keycolumn = True
        columns += 1
    #
    trs = [ ]
    th = [ ]
    if keycolumn:
        th.append(apodhtml.htmlelem(tag="th",content=ent["keyhead"]))
    for bit in range(brange["max"],brange["min"]-1,-1):
        th.append(apodhtml.htmlelem(tag="th",content=("Bit "+str(bit))))
    trs.append(apodhtml.htmlelem(tag="tr",attr={ "class": "apodbitfieldtablehead" },content=th))
    #
    if "bitrows" in ent:
        rows = [ ]
        for brow in ent["bitrows"]:
            rowo = { "fieldarr": brow["bitfields"], "fielddsp": brow["bitdisplay"] }
            if "keyval" in brow:
                rowo["keyval"] = brow["keyval"]
            rows.append(rowo)
    else:
        rowo = { "fieldarr": ent["bitfields"], "fielddsp": ent["bitdisplay"] }
        if "keyval" in ent:
            rowo["keyval"] = ent["keyval"]
        rows = [ rowo ]
    #
    for row in rows:
        fieldarr = row["fieldarr"]
        fielddsp = row["fielddsp"]
        #
        pbr = -1
        bit = brange["max"]
        bitcol = bit # HTML table column
        tr = [ ]
        if keycolumn:
            keyf = ""
            if "keyval" in row:
                keyf = row["keyval"]
            #
            tr.append(apodhtml.htmlelem(tag="th",attr={ "class": "apodbitfieldtablerowkey" },content=keyf))
        while bit >= brange["min"]:
            br = fielddsp[bit]
            bmax = bmin = bit
            bit = bit - 1
            while bit >= brange["min"] and type(fielddsp[bit]) == type(br) and fielddsp[bit] == br:
                bmin = bit
                bit = bit - 1
            #
            if type(br) == bool and br == False: # nothing in this part
                attr = { "class": "apodbitfieldtablenodef" }
                if (bmax-bmin) > 0:
                    attr["colspan"] = str(bmax+1-bmin)
                #
                tr.append(apodhtml.htmlelem(tag="td",attr=attr))
            else: # content as normal
                bent = fieldarr[br]
                if not bmax == bent["max"] or not bmin == bent["min"]:
                    raise Exception("Error in bitdisplay vs bitfields")
                #
                attr = { "class": "apodbitfieldtablecol" }
                if (bmax-bmin) > 0:
                    attr["colspan"] = str(bmax+1-bmin)
                #
                subdcon = [ ]
                tablecoltohtml(subdcon,tcolo,bent["value"],compiled_format)
                tr.append(apodhtml.htmlelem(tag="td",attr=attr,content=subdcon))
        #
        trs.append(apodhtml.htmlelem(tag="tr",attr={ "class": "apodbitfieldtablerow" },content=tr))
    #
    dcon.append(apodhtml.htmlelem(tag="table",attr={ "class": "apodbitfieldtable", "style": ("width: "+str(colwidth*columns)+"em;") },content=trs))

# dcon = array of elements to write
# tcolo = column table info
# dcolo = column
def tablecoltohtml(dcon,tcolo,dcolo,compiled_format):
    if compiled_format == "array" or compiled_format == "array/range":
        if not type(dcolo) == list:
            raise Exception("array column not array")
        # each array of the element is an array containing a single value,
        # or two values to signify a range. perhaps the two value array should
        # just be an object that says "I'm a range"
        entc = 0
        for ent in dcolo:
            if entc > 0:
                if "array separator" in tcolo:
                    dcon.append(tcolo["array separator"])
                else:
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
                dcon.append(apodhtml.htmlelem(tag="span",content=tablecolinttohtml(tcolo,ent[0])))
            elif len(ent) == 2 and compiled_format == "array/range":
                dcon.append(apodhtml.htmlelem(tag="span",content=(tablecolinttohtml(tcolo,ent[0])+"-"+tablecolinttohtml(tcolo,ent[1]))))
            else:
                print(ent)
                raise Exception("array ent is array with wrong number of elements")
            entc = entc + 1
    elif compiled_format == "normal":
        if isinstance(dcolo,str):
            dcon.append(dcolo)
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
    elif compiled_format == "array/combined":
        raise Exception("Calling function is supposed to take care of array/combined (BUG)")
    elif compiled_format == "array/formatting":
        if not type(dcolo) == list:
            raise Exception("formatting not array")
        for ent in dcolo:
            if ent["type"] == "text":
                tablecoltohtml(dcon,tcolo,ent["text"],tcolo["compiled format:array/formatting"])
            elif ent["type"] == "bold":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="b",content=subdcon))
            elif ent["type"] == "italic":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="i",content=subdcon))
            elif ent["type"] == "underline":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="u",content=subdcon))
            elif ent["type"] == "strikethrough":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="s",content=subdcon))
            elif ent["type"] == "superscript":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="sup",content=subdcon))
            elif ent["type"] == "subscript":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="sub",content=subdcon))
            elif ent["type"] == "monospace":
                for subi in ent["sub"]:
                    subdcon = [ ]
                    tablecoltohtml(subdcon,tcolo,[ subi ],compiled_format)
                    dcon.append(apodhtml.htmlelem(tag="span",attr={ "class": "fmtmonospace" },content=subdcon))
            elif ent["type"] == "weblink":
                nfo = ent["info"]
                if "url" in nfo:
                    dcon.append(apodhtml.htmlelem(tag="a",attr={ "href": nfo["url"], "target": "_blank" },content=nfo["text"]))
            elif ent["type"] == "link":
                nfo = ent["info"]
                if "type" in nfo:
                    if nfo["type"] == "table":
                        dcon.append(apodhtml.htmlelem(tag="a",attr={ "href": ("tables-"+nfo["id"]+".html") },content=nfo["text"]))
                    else:
                        print(ent)
                        raise Exception("Unknown link type "+nfo["type"])
                else:
                    print(ent)
                    raise Exception("Missing type in link")
            elif ent["type"] == "bitfield":
                tablecolbitfieldtohtml(dcon,tcolo,ent,compiled_format)
            elif ent["type"] == "enum":
                tablecolenumtohtml(dcon,tcolo,ent,compiled_format)
            else:
                print(ent)
                raise Exception("Unknown formatting obj")
    else:
        print("Warning: Unsupported compiled format "+compiled_format)

def genfrag_table(bookid,ji):
    def genhtmlentrytags(coli,colidx,subdcon,combent,combenttags,compiled_format):
        if coli == colidx or (compiled_format == "array/combined" and type(dcolo) == list and len(dcolo) > 1):
            tg = [ ]
            plus = False
            keyord = list(combenttags.keys())
            keyord.sort(key=lambda x: x.lower())
            for key in keyord:
                if key == "": # used to indicate data without a tag
                    plus = True
                else:
                    tg += ["(", key, ")"]
            if len(tg) > 0:
                if plus == True:
                    tg += ["+"]
            subdcon.append(apodhtml.htmlelem(tag="sup",attr={ "class": "apodenttag" },content=tg))
    #
    def genhtmlsourceindex(coli,colidx,subdcon,ji,combent,combentsi,compiled_format):
        for sil in combentsi:
            tg = [ ]
            if coli == colidx or (compiled_format == "array/combined" and type(dcolo) == list and len(dcolo) > 1):
                # if this is the column to emit references, do it, but only if not all sources agree
                if "source index" in combent and not len(combent["source index"]) == len(ji["sources"]):
                    tg += ["[", str(sil+1), "]"]
                if len(tg) > 0:
                    subdcon.append(apodhtml.htmlelem(tag="sup",content=apodhtml.htmlelem(tag="a",attr={ "href": ("#"+apodhtml.mkhtmlid("table-sr",bookid+":"+str(sil+1))), "class": "apodsourceidxref" },content=tg)))
    #
    hw = apodhtml.htmlwriter()
    hw.write(apodhtml.htmlelem(tag="a",attr={ "id": apodhtml.mkhtmlid("table",bookid) }))
    hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodtitle", "title": bookid },content=ji["table"]))
    if "description" in ji:
        hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apoddescription" },content=ji["description"]))
    if "table columns" in ji and "rows" in ji:
        hw.begin(apodhtml.htmlelem(tag="table",attr={ "class": "apodtable" }))
        # header
        hw.begin(apodhtml.htmlelem(tag="tr",attr={ "class": "apodtablehead" }))
        for colo in ji["table columns"]:
            title = ""
            if "title" in colo:
                title = colo["title"]
            hw.write(apodhtml.htmlelem(tag="th",content=title))
        #
        hw.end() # th
        # which column to attach tags to? default: last column
        tagcolidx = len(ji["table columns"]) - 1
        if "tags on column" in ji:
            tagcolidx = ji["tags on column"]
        # which column to attach source ref to? default: last column
        refcolidx = len(ji["table columns"]) - 1
        if "source refs on column" in ji:
            refcolidx = ji["source refs on column"]
        # rows
        for rowo in ji["rows"]:
            if not "data" in rowo:
                continue
            hw.begin(apodhtml.htmlelem(tag="tr",attr={ "class": "apodtablerow" }))
            for coli in range(0,len(rowo["data"])):
                attr = { }
                tcolo = ji["table columns"][coli]
                dcolo = rowo["data"][coli]
                dcon = [ ]
                #
                if "nowrap" in tcolo and tcolo["nowrap"] == True:
                    attr["class"] = "nowrap"
                #
                if tcolo["compiled format"] == "array/combined":
                    combentcount = 0
                    for combent in dcolo: # require value and source index or else fault!
                        if combentcount > 0: # TODO: Obey the "array separator" spec in the table whether the table should separate by space or a line break
                            dcon.append(apodhtml.htmlelem(tag="div",attr={ "style": "height: 0.5em;" },content="")) # space them out vertically so they are not jumbled
                        #
                        subdcon = [ ]
                        #
                        tablecoltohtml(subdcon,tcolo,combent["value"],tcolo["compiled format:array/combined"])
                        genhtmlentrytags(coli=coli,colidx=tagcolidx,subdcon=subdcon,combent=combent,combenttags=combent["entry tags"],compiled_format=tcolo["compiled format"])
                        genhtmlsourceindex(coli=coli,colidx=refcolidx,subdcon=subdcon,ji=ji,combent=combent,combentsi=combent["source index"],compiled_format=tcolo["compiled format"])
                        #
                        dcon.append(apodhtml.htmlelem(tag="div",attr={ "class": "apodarrcmbent" },content=subdcon))
                        combentcount = combentcount + 1
                else:
                    tablecoltohtml(dcon,tcolo,dcolo,tcolo["compiled format"])
                    genhtmlentrytags(coli=coli,colidx=tagcolidx,subdcon=dcon,combent=rowo,combenttags=rowo["entry tags"],compiled_format=tcolo["compiled format"])
                    genhtmlsourceindex(coli=coli,colidx=refcolidx,subdcon=dcon,ji=ji,combent=rowo,combentsi=rowo["source index"],compiled_format=tcolo["compiled format"])
                #
                hw.write(apodhtml.htmlelem(tag="td",attr=attr,content=dcon))
            #
            hw.end() # tr
        # end
        hw.end() # table
        #
        uli = [ ]
        for colo in ji["table columns"]:
            desc = ""
            title = ""
            if "title" in colo:
                title = colo["title"]
            if "description" in colo:
                desc = colo["description"]
            if not title == "" and not desc == "":
                uli.append(apodhtml.htmlelem(tag="li",content=[ apodhtml.htmlelem(tag="b",content=title), ": ", apodhtml.htmlelem(tag="span",content=desc) ]))
        if len(uli) > 0:
            nc = [ apodhtml.htmlelem(tag="span",attr={ "class": "apodnoteshead" },content="Columns:"), apodhtml.htmlelem(tag="ul",attr={ "class": "apodnoteslist" },content=uli) ]
            hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodnotes" },content=nc))
        #
    #
    uli = [ ]
    if "notes" in ji:
        nl = ji["notes"]
        if not type(nl) == list:
            nl = [ nl ]
        for nent in nl:
            uli.append(apodhtml.htmlelem(tag="li",content=nent))
    if "sources" in ji:
        sl = ji["sources"]
        for se in sl:
            if "notes" in se:
                nl = se["notes"]
                if not type(nl) == list:
                    nl = [ nl ]
                for nent in nl:
                    ncon = [ ]
                    if "entry tag" in se:
                        ncon.append(apodhtml.htmlelem(tag="span",attr={ "class": "apodenttag" },content=("("+se["entry tag"]+") ")))
                    ncon.append(nent)
                    uli.append(apodhtml.htmlelem(tag="li",content=ncon))
    if len(uli) > 0:
        nc = [ apodhtml.htmlelem(tag="span",attr={ "class": "apodnoteshead" },content="Notes:"), apodhtml.htmlelem(tag="ul",attr={ "class": "apodnoteslist" },content=uli) ]
        hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodnotes", "title": bookid },content=nc))
    #
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
                print(sel)
                raise Exception("source object, no source in "+bookid+"?")
            src = sel["source"]
            if not type(src) == dict:
                raise Exception("source element source not object")
            if not "id" in src:
                print(src)
                raise Exception("source object, no id in "+bookid+"?")
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
            nent.append(apodhtml.htmlelem(tag="sup",content=apodhtml.htmlelem(tag="a",attr={ "href": ("sources-"+src["id"]+".html"), "class": "apodsourceidx" },content=("["+str(sil+1)+"]"))))
            #
            url = None
            if "url" in sref:
                url = sref["url"]
            if "url" in src:
                url = src["url"]
            if not url == None and not url == "":
                nent.append(apodhtml.htmlelem(tag="br"))
                nent.append(apodhtml.htmlelem(tag="a",attr={ "class": "apodsourceurl", "target": "_blank", "href": url },content=apodhtml.unescapeurl(url)))
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
                            srctref = "sources-"+src["id"]+".html"
                            srctref += "#" + apodhtml.mkhtmlid("source",src["id"],path)
                            l.append(apodhtml.htmlelem(tag="span",content='"'))
                            l.append(apodhtml.htmlelem(tag="a",attr={ "class": "apodsourcepreftitle", "href": srctref },content=pref["title"]))
                            l.append(apodhtml.htmlelem(tag="span",content='"'))
                        if "page" in pref:
                            if not len(l) == 0:
                                l.append(", ")
                            l.append(apodhtml.htmlelem(tag="span",attr={ "class": "apodsourceprefpage" },content=("(page "+str(pref["page"])+")")))
                    if not l == None:
                        nent.append(apodhtml.htmlelem(tag="br"))
                        nent.append(apodhtml.htmlelem(tag="span",attr={ "class": "apodsourcepref" },content=l))
            #
            if "notes" in src:
                nent.append(apodhtml.htmlelem(tag="br"))
                nent.append(apodhtml.htmlelem(tag="span",content=[ "Notes: ", src["notes"] ]))
            #
            if "source json file" in sel:
                nent.append(apodhtml.htmlelem(tag="br"))
                nent.append(apodhtml.htmlelem(tag="span",content=[ "JSON: ", sel["source json file"] ]))
            #
            uli.append(apodhtml.htmlelem(tag="li",attr={ "class": "apodsourceref", "id": apodhtml.mkhtmlid("table-sr",bookid+":"+str(sil+1)) },content=nent))
        #
        nc = [ apodhtml.htmlelem(tag="span",attr={ "class": "apodsourceshead" },content="Sources:"), apodhtml.htmlelem(tag="ul",attr={ "class": "apodsourceslist" },content=uli) ]
        hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodsources", "title": bookid },content=nc))
    if "source json file" in ji:
        uli = [ apodhtml.htmlelem(tag="li",content=ji["source json file"]) ]
        nc = [ apodhtml.htmlelem(tag="span",attr={ "class": "apodsourcejsonfile" },content="JSON:"), apodhtml.htmlelem(tag="ul",attr={ "class": "apodsourceslist" },content=uli) ]
        hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodsources", "title": bookid },content=nc))
    r = hw.get()
    return r

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
    path = "compiled/html/sources-"+bookid+".html"
    f = open(path,"wb")
    writewhole_beginhead(f)
    if "title" in ji:
        f.write(("<title>"+apodhtml.htmlescape(ji["title"])+"</title>").encode('UTF-8'))
    f.write(("<link rel=\"stylesheet\" href=\"sources.css\" />").encode('UTF-8'))
    writewhole_endhead(f)
    writewhole_beginbody(f)
    f.write(htmlfrag)
    writewhole_endbody(f)
    f.close()

def writewhole_table(bookid,ji,htmlfrag):
    path = "compiled/html/tables-"+bookid+".html"
    f = open(path,"wb")
    writewhole_beginhead(f)
    if "title" in ji:
        f.write(("<title>"+apodhtml.htmlescape(ji["title"])+"</title>").encode('UTF-8'))
    f.write(("<link rel=\"stylesheet\" href=\"tables.css\" />").encode('UTF-8'))
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
    writewhole_table(ji["id"],ji,htmlfrag)
    #
    title = ji["id"]
    if "table" in ji:
        title = englishpp(ji["table"])
    tableproclist.append({ "id": ji["id"], "title": title })
#
tableproclist.sort(key=tableprocsort)

# make overall source list HTML too
f = open("compiled/html/sources.html","wb")
writewhole_beginhead(f)
f.write("<title>Sources</title>".encode('UTF-8'))
f.write(("<link rel=\"stylesheet\" href=\"sources.css\" />").encode('UTF-8'))
writewhole_endhead(f)
writewhole_beginbody(f)
#
for sobj in sourceproclist:
    hw = apodhtml.htmlwriter()
    le = apodhtml.htmlelem(tag="a",attr={ "href": ("sources-"+sobj["id"]+".html"), "title": sobj["id"], "class": "apodsourceslisttitle" },content=sobj["title"])
    hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodsourceslistent" },content=le))
    f.write(hw.get())
writewhole_endbody(f)
f.close()

# make overall table list HTML too
f = open("compiled/html/tables.html","wb")
writewhole_beginhead(f)
f.write("<title>Tables</title>".encode('UTF-8'))
f.write(("<link rel=\"stylesheet\" href=\"tables.css\" />").encode('UTF-8'))
writewhole_endhead(f)
writewhole_beginbody(f)
#
for sobj in tableproclist:
    hw = apodhtml.htmlwriter()
    le = apodhtml.htmlelem(tag="a",attr={ "href": ("tables-"+sobj["id"]+".html"), "title": sobj["id"], "class": "apodtableslisttitle" },content=sobj["title"])
    hw.write(apodhtml.htmlelem(tag="div",attr={ "class": "apodtableslistent" },content=le))
    f.write(hw.get())
writewhole_endbody(f)
f.close()

# cascading stylesheet too
sf = open("sources.html.css","rb")
df = open("compiled/html/sources.css","wb")
df.write(sf.read())
df.close()
sf.close()
# cascading stylesheet too
sf = open("tables.html.css","rb")
df = open("compiled/html/tables.css","wb")
df.write(sf.read())
df.close()
sf.close()
