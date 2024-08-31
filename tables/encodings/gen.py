#!/usr/bin/python3

import os
import re
import sys
import csv
import math
import base64

# cp437
cp437_control_codes = [
        # byte value, unicode point
        [ 0x01, 0x263A ], # smiley
        [ 0x02, 0x263B ], # smiley
        [ 0x03, 0x2665 ], # heart
        [ 0x04, 0x2666 ], # diamond
        [ 0x05, 0x2663 ], # club
        [ 0x06, 0x2660 ], # spade
        [ 0x07, 0x2022 ], # dot
        [ 0x08, 0x25D8 ], # dot
        [ 0x09, 0x25CB ], # circle
        [ 0x0A, 0x25D9 ], # circle
        [ 0x0B, 0x2642 ], # male symbol
        [ 0x0C, 0x2640 ], # female symbol
        [ 0x0D, 0x266A ], # music note
        [ 0x0E, 0x266B ], # music note
        [ 0x0F, 0x263C ], # sun
        [ 0x10, 0x25BA ], # right triangle arrow
        [ 0x11, 0x25C4 ], # left triangle arrow
        [ 0x12, 0x2195 ], # double vertical arrow
        [ 0x13, 0x203C ], # double exclamation mark
        [ 0x14, 0x00B6 ], # paragraph
        [ 0x15, 0x00A7 ], # section
        [ 0x16, 0x25AC ], # black rectangle
        [ 0x17, 0x21A8 ], # up-down arrow with base
        [ 0x18, 0x2191 ], # up arrow
        [ 0x19, 0x2193 ], # down arrow
        [ 0x1A, 0x2192 ], # right arrow
        [ 0x1B, 0x2190 ], # left arrow
        [ 0x1C, 0x221F ], # right angle
        [ 0x1D, 0x2194 ], # double horizontal arrow
        [ 0x1E, 0x25B2 ], # triangle arrow up
        [ 0x1F, 0x25BC ], # triangle arrow down
        [ 0x7F, 0x2302 ]
]

# cp932
cp932_replaced_codes = [
        # byte value, unicode point
        [ 0x5C, 0x00A5 ], # yen
        [ 0x7E, 0x203E ]  # overline
]
cp932_control_codes = [
        # byte value, unicode point
        [ 0x00, 0x2400 ],
        [ 0x01, 0x2401 ],
        [ 0x02, 0x2402 ],
        [ 0x03, 0x2403 ],
        [ 0x04, 0x2404 ],
        [ 0x05, 0x2405 ],
        [ 0x06, 0x2406 ],
        [ 0x07, 0x2407 ],
        [ 0x08, 0x2408 ],
        [ 0x09, 0x2409 ],
        [ 0x0A, 0x240A ],
        [ 0x0B, 0x240B ],
        [ 0x0C, 0x240C ],
        [ 0x0D, 0x240D ],
        [ 0x0E, 0x240E ],
        [ 0x0F, 0x240F ],
        [ 0x10, 0x2410 ],
        [ 0x11, 0x2411 ],
        [ 0x12, 0x2412 ],
        [ 0x13, 0x2413 ],
        [ 0x14, 0x2414 ],
        [ 0x15, 0x2415 ],
        [ 0x16, 0x2416 ],
        [ 0x17, 0x2417 ],
        [ 0x18, 0x2418 ],
        [ 0x19, 0x2419 ],
        [ 0x1A, 0x241A ],
        [ 0x1B, 0x241B ],
        [ 0x1C, 0x241C ],
        [ 0x1D, 0x241D ],
        [ 0x1E, 0x241E ],
        [ 0x1F, 0x241F ],
        [ 0x7F, 0x2421 ]
]
apple_roman_patch = [
        { "byteseq": bytes([0xF0]), "name": "Apple logo", "display image": "ref/Apple_logo_black.svg" }
]

def patch_cp437_control_codes(m):
    # CP437 has well known symbols in the range 0-31 inclusive which
    # this code will patch in now.
    global cp437_control_codes
    for ent in cp437_control_codes:
        m[ent[0]].unicp = [ ent[1] ]
        if not ent[1] == None:
            m[ent[0]].display = chr(ent[1])

def patch_shiftjis_control_codes(m):
    # Unicode list forgot to list that backslash was replaced by Yen (which is why
    # Japanese systems have such strange looking DOS prompts) and tilde by a
    # top horizontal line.
    global cp932_control_codes
    for ent in cp932_control_codes:
        m[ent[0]].unicp = [ ent[1] ]
        if not ent[1] == None:
            m[ent[0]].display = chr(ent[1])

def patch_shiftjis_replaced_ascii_codes(m):
    # Unicode list forgot to list that backslash was replaced by Yen (which is why
    # Japanese systems have such strange looking DOS prompts) and tilde by a
    # top horizontal line.
    global cp932_replaced_codes
    for ent in cp932_replaced_codes:
        m[ent[0]].unicp = [ ent[1] ]
        if not ent[1] == None:
            m[ent[0]].display = chr(ent[1])

def is_newer_than(source,dest):
    if not os.path.exists(source):
        return False
    if not os.path.exists(dest):
        return True
    so = os.lstat(source)
    do = os.lstat(dest)
    return so.st_mtime > do.st_mtime

class UnicodeMapEntry:
    displayImage = None
    display = None
    byteseq = None
    unicp = None
    name = None
    def __init__(self):
        True
    def getHexString(self):
        r = ""
        for i in self.byteseq:
            if not r == "":
                r += " "
            s = hex(i)[2:]
            while len(s) < 2:
                s = '0' + s
            r += s
        return r
    def getDecString(self):
        r = ""
        for i in self.byteseq:
            if not r == "":
                r += " "
            s = str(i)
            while len(s) < 3:
                s = ' ' + s
            r += s
        return r
    def getOctString(self):
        r = ""
        for i in self.byteseq:
            if not r == "":
                r += " "
            s = oct(i)[2:]
            while len(s) < 3:
                s = '0' + s
            r += s
        return r
    def getBinString(self):
        r = ""
        for i in self.byteseq:
            if not r == "":
                r += " "
            s = bin(i)[2:]
            while len(s) < 8:
                s = '0' + s
            r += s
        return r
    def getUnicpString(self):
        unicp_s = ""
        if not self.unicp == None:
            for us in self.unicp:
                if not unicp_s == "":
                    unicp_s += " "
                us = hex(us)[2:]
                while len(us) < 4:
                    us = '0' + us
                unicp_s += us
        #
        return unicp_s
    def getDisplayString(self):
        disp = ''
        if not self.display == None:
            disp = self.display
        return disp

def load_unicode_mapping_file(path):
    ret = { }
    f = open(path,"r",encoding="ascii") # At no time does the list deviate from ASCII (prove me wrong!)
    for l in f.readlines():
        l = l.strip(' \t\n\r')
        if len(l) == 0:
            continue
        if l[0] == '#':
            continue
        t1 = re.split(r'#',l)
        if len(t1) < 2:
            continue
        t11 = re.split(r'[ \t]+',t1[0].strip())
        if len(t11) < 2:
            continue
        l = t11 + [ t1[1] ]
        # <hex byte(s)> <unicode code point> <name>
        hbstr = t11[0]
        unicp = t11[1]
        name = t1[1].strip()
        if not hbstr[0:2] == "0x":
            continue
        hbstr = hbstr[2:]
        key = int(hbstr,16)
        bvl = len(hbstr)
        if (bvl & 1) > 0:
            continue
        bvl = bvl >> 1
        if bvl == 0:
            continue
        bv = bytearray(bvl)
        for i in range(0,bvl):
            ss = hbstr[i*2:(i+1)*2]
            bv[i] = int("0x"+ss,16)
        #
        ent = UnicodeMapEntry()
        ent.unicp = [ ]
        for uas in unicp.split("+"):
            if not uas[0:2] == "0x":
                continue
            ent.unicp.append(int(uas[2:],16))
        #
        ent.byteseq = bv
        ent.name = name
        ent.display = None
        if len(ent.unicp) > 0:
            ent.display = ""
            for u in ent.unicp:
                if not (u < 0x20 or (u >= 0x7F and u <= 0x9F)):
                    ent.display += chr(u)
        #
        ret[key] = ent
        #
    f.close()
    return ret

def write_standard_csv_header(csw,title="UNTITLED"):
    csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
    csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
    csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
    csw.writerow([title, '#table-title'])
    csw.writerow([])

def write_standard_csv_table(csw,map_table):
    for enti in sorted(map_table.keys()):
        ent = map_table[enti]
        vhex = ent.getHexString()
        vdec = ent.getDecString()
        voct = ent.getOctString()
        vbin = ent.getBinString()
        unicp_s = ent.getUnicpString()
        disp_s = ent.getDisplayString()
        csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])

def my_htmlescape(x):
    r = ''
    for c in x:
        if c == '<':
            r += '&lt;'
        elif c == '>':
            r += '&gt;'
        elif c == '&':
            r += '&amp;'
        else:
            r += c
    return r

def hex_prepend_0x(x):
    r = ""
    for h in re.split(r" +",x):
        if h == "":
            continue
        if not r == "":
            r += " "
        r += "0x"+str(h)
    return r

def b_detect_imagetype(b):
    if b[0:4] == b'\x89PNG':
        return "image/png"
    if b[0:4] == b'<svg':
        return "image/svg+xml"
    #
    return None

def write_standard_html_file(html_file,map_table):
    # this code ASSUMES the entries are already in byte value order, as the .TXT files are
    hf = open(html_file,mode="w",encoding="utf-8",newline="\n")
    hf.write("<!DOCTYPE html>\n<html><head>")
    hf.write("<meta charset=\"UTF-8\">")
    hf.write("<style>\n")
    hf.write("th, td { padding: 0; padding-left: 0.5em; padding-right: 0.5em; margin: 0; margin-left: 0.35em; margin-right: 0.35em; }\n")
    hf.write("th { color: white; background-color: black; font-weight: 900; padding-top: 0.25em; padding-bottom: 0.25em; }\n")
    hf.write("td { border-right: 1px solid black; height: 1.75em; }\n")
    hf.write("td.rightmost { border-right: none; }\n")
    hf.write("th.ral, td.ral { text-align: right; }\n")
    hf.write("td.hexdigit { font-family: monospace; font-size: 1em; }\n")
    hf.write("tr { padding: 0; margin: 0; background-color: white; }\n")
    hf.write("tr.oddline { background-color: #DDDDDD; }\n")
    hf.write("tr:hover { background-color: #DDDDFF; }\n")
    hf.write("</style>")
    hf.write("</head><body>")
    hf.write("<table style=\"text-align: left; padding: 0; margin: 0; border-spacing: 0; border: 1px solid black;\">")
    #
    hf.write("<tr>")
    hf.write("<th>Display</th>")
    hf.write("<th class=\"ral\">Hex</th>")
    hf.write("<th class=\"ral\">Dec</th>")
    hf.write("<th class=\"ral\">Unicode</th>")
    hf.write("<th>Name</th>")
    hf.write("</tr>")
    #
    count = 0
    for enti in sorted(map_table.keys()):
        ent = map_table[enti]
        vhex = ent.getHexString()
        vdec = ent.getDecString()
        unicp_s = ent.getUnicpString()
        disp_s = ent.getDisplayString()
        #
        hf.write("<tr")
        if (count % 2) == 1:
            hf.write(" class=\"oddline\"")
        hf.write(">")
        if not ent.displayImage == None:
            f = open(ent.displayImage,"rb")
            b = f.read()
            f.close()
            imgmime = b_detect_imagetype(b)
            hf.write("<td class=\"\"><img style=\"width:1em;\" src=\"data:"+imgmime+";base64,"+base64.b64encode(b).decode('ascii')+"\"/></td>")
        else:
            hf.write("<td class=\"\">"+my_htmlescape(disp_s)+"</td>")
        hf.write("<td class=\"ral hexdigit\">"+hex_prepend_0x(my_htmlescape(vhex).upper())+"</td>")
        hf.write("<td class=\"ral\">"+my_htmlescape(vdec)+"</td>")
        hf.write("<td class=\"ral hexdigit\">"+hex_prepend_0x(my_htmlescape(unicp_s).upper())+"</td>")
        hf.write("<td class=\"rightmost\">"+my_htmlescape(ent.name)+"</td>")
        hf.write("</tr>")
        #
        count += 1
    #
    hf.write("</table>")
    hf.write("</body></html>")
    hf.close()

map_cp437 = load_unicode_mapping_file("ref/CP437.TXT")
# CP437 is the same as ASCII for the first 128 entries.
# The Unicode consortium list always treats 0-31 inclusive as control codes
# even though CP437 has well known symbols in that range.
map_ascii = { }
for key in map_cp437:
    if key < 128:
        map_ascii[key] = map_cp437[key]
#
patch_cp437_control_codes(map_cp437)

todolist = [
    { "maplist": map_ascii,                   "dest": "gen-ascii.csv",                            "title": "ASCII table" },
    { "source": "ref/CP037.TXT",              "dest": "gen-ebcdic-cp037.csv",                     "title": "IBM EBCDIC US/Canada table" },
    { "maplist": map_cp437,                   "dest": "gen-cp437.csv",                            "title": "Microsoft/IBM PC Code Page 437 table (Latin US)" },
    { "source": "ref/CP737.TXT",              "dest": "gen-cp737.csv",                            "title": "Microsoft/IBM PC Code Page 737 table (Greek)", "patch437ctrl": True },
    { "source": "ref/CP775.TXT",              "dest": "gen-cp775.csv",                            "title": "Microsoft/IBM PC Code Page 775 table (Baltic Rim)", "patch437ctrl": True },
    { "source": "ref/CP850.TXT",              "dest": "gen-cp850.csv",                            "title": 'Microsoft/IBM PC Code Page 850 table (Latin 1)', "patch437ctrl": True },
    { "source": "ref/CP852.TXT",              "dest": "gen-cp852.csv",                            "title": "Microsoft/IBM PC Code Page 852 table (Latin 2)", "patch437ctrl": True },
    { "source": "ref/CP855.TXT",              "dest": "gen-cp855.csv",                            "title": "Microsoft/IBM PC Code Page 855 table (Cyrillic)", "patch437ctrl": True },
    { "source": "ref/CP856.TXT",              "dest": "gen-cp856.csv",                            "title": "Microsoft/IBM PC Code Page 856 table (Hebrew)", "patch437ctrl": True },
    { "source": "ref/CP857.TXT",              "dest": "gen-cp857.csv",                            "title": "Microsoft/IBM PC Code Page 857 table (Turkish)", "patch437ctrl": True },
    { "source": "ref/CP860.TXT",              "dest": "gen-cp860.csv",                            "title": "Microsoft/IBM PC Code Page 860 table (Portuguese)", "patch437ctrl": True },
    { "source": "ref/CP861.TXT",              "dest": "gen-cp861.csv",                            "title": "Microsoft/IBM PC Code Page 861 table (Icelandic)", "patch437ctrl": True },
    { "source": "ref/CP862.TXT",              "dest": "gen-cp862.csv",                            "title": "Microsoft/IBM PC Code Page 862 table (Hebrew)", "patch437ctrl": True },
    { "source": "ref/CP863.TXT",              "dest": "gen-cp863.csv",                            "title": "Microsoft/IBM PC Code Page 863 table (French Canadian)", "patch437ctrl": True },
    { "source": "ref/CP864.TXT",              "dest": "gen-cp864.csv",                            "title": "Microsoft/IBM PC Code Page 864 table (Arabic)", "patch437ctrl": True },
    { "source": "ref/CP865.TXT",              "dest": "gen-cp865.csv",                            "title": "Microsoft/IBM PC Code Page 865 table (Nordic)", "patch437ctrl": True },
    { "source": "ref/CP866.TXT",              "dest": "gen-cp866.csv",                            "title": "Microsoft/IBM PC Code Page 866 table (Russian)", "patch437ctrl": True },
    { "source": "ref/CP869.TXT",              "dest": "gen-cp869.csv",                            "title": "Microsoft/IBM PC Code Page 869 table (Greek)", "patch437ctrl": True },
    { "source": "ref/CP874.TXT",              "dest": "gen-cp874.csv",                            "title": "Microsoft/IBM PC Code Page 874 table (Thai)", "patch437ctrl": True },
    { "source": "ref/CP932.TXT",              "dest": "gen-cp932.csv",                            "title": "Microsoft/IBM PC Code Page 932 table (Shift JIS)", "patch932ctrl": True, "patchsjisascii": True },
    { "source": "ref/CP936.TXT",              "dest": "gen-cp936.csv",                            "title": "Microsoft/IBM PC Code Page 936 table (GBK)" },
    { "source": "ref/CP949.TXT",              "dest": "gen-cp949.csv",                            "title": "Microsoft/IBM PC Code Page 949 table (Unified Hangul)" },
    { "source": "ref/CP950.TXT",              "dest": "gen-cp950.csv",                            "title": "Microsoft/IBM PC Code Page 950 table (Chinese Big 5)" },
    { "source": "ref/CP1250.TXT",             "dest": "gen-cp1250.csv",                           "title": "Microsoft Windows Code Page 1250 (Central/Eastern Europe)" },
    { "source": "ref/CP1251.TXT",             "dest": "gen-cp1251.csv",                           "title": "Microsoft Windows Code Page 1251 (Cyrillic)" },
    { "source": "ref/CP1252.TXT",             "dest": "gen-cp1252.csv",                           "title": "Microsoft Windows Code Page 1252 (Latin ISO 8859-1)" },
    { "source": "ref/CP1253.TXT",             "dest": "gen-cp1253.csv",                           "title": "Microsoft Windows Code Page 1253 (Greek)" },
    { "source": "ref/CP1254.TXT",             "dest": "gen-cp1254.csv",                           "title": "Microsoft Windows Code Page 1254 (Turkish)" },
    { "source": "ref/CP1255.TXT",             "dest": "gen-cp1255.csv",                           "title": "Microsoft Windows Code Page 1255 (Hebrew)" },
    { "source": "ref/CP1256.TXT",             "dest": "gen-cp1256.csv",                           "title": "Microsoft Windows Code Page 1256 (Arabic)" },
    { "source": "ref/CP1257.TXT",             "dest": "gen-cp1257.csv",                           "title": "Microsoft Windows Code Page 1257 (Estonian, Latvian, Lithuanian, and more)" },
    { "source": "ref/CP1258.TXT",             "dest": "gen-cp1258.csv",                           "title": "Microsoft Windows Code Page 1258 (Vietnamese)" },
    { "source": "ref/MAC-ROMAN.TXT",          "dest": "gen-apple-mac-roman.csv",                  "title": "Apple Macintosh MacRoman table", "patch": apple_roman_patch },
    { "source": "ref/MAC-ARABIC.TXT",         "dest": "gen-apple-mac-arabic.csv",                 "title": "Apple Macintosh Arabic table" },
    { "source": "ref/MAC-ARMENIAN.TXT",       "dest": "gen-apple-mac-armenian.csv",               "title": "Apple Macintosh Armenian table" },
    { "source": "ref/MAC-BARENCYR.TXT",       "dest": "gen-apple-mac-barents-cyrillic.csv",       "title": "Apple Macintosh Barents Cyrillic table" },
    { "source": "ref/MAC-CYRILLIC.TXT",       "dest": "gen-apple-mac-cyrillic.csv",               "title": "Apple Macintosh Cyrillic table" },
    { "source": "ref/MAC-CELTIC.TXT",         "dest": "gen-apple-mac-celtic.csv",                 "title": "Apple Macintosh Celtic table" }
]

for todo in todolist:
    ref_file = __file__
    if "source" in todo:
        ref_file = todo["source"]
    csv_file = None
    if "dest" in todo:
        csv_file = todo["dest"]
    map_list = None
    if "maplist" in todo:
        map_list = todo["maplist"]
    title = "UNTITLED"
    if "title" in todo:
        title = todo["title"]
    #
    if ref_file == None or csv_file == None:
        continue
    if not is_newer_than(source=ref_file,dest=csv_file):
        continue
    #
    if map_list == None:
        map_list = load_unicode_mapping_file(ref_file)
        if todo.get("patch437ctrl") == True:
            patch_cp437_control_codes(map_list)
        if todo.get("patch932ctrl") == True:
            patch_shiftjis_control_codes(map_list)
        if todo.get("patchsjisascii") == True:
            patch_shiftjis_replaced_ascii_codes(map_list)
    #
    if "patch" in todo:
        p = todo["patch"]
        for patch in p:
            key = ""
            bseq = None
            if "byteseq" in patch:
                byt = patch["byteseq"]
                k = None
                for b in byt:
                    if k == None:
                        k = 0
                    k = (k << 8) + b
                bseq = byt
                key = k
            if not key == None:
                if not key in map_list:
                    map_list[key] = UnicodeMapEntry()
                    map_list[key].byteseq = bseq
                if "name" in patch:
                    map_list[key].name = patch["name"]
                if "display image" in patch:
                    map_list[key].displayImage = patch["display image"]
    #
    f = open(csv_file,mode="w",encoding="utf-8",newline="")
    csw = csv.writer(f)
    write_standard_csv_header(csw,title=title)
    write_standard_csv_table(csw,map_list)
    f.close()
    #
    html_file = re.sub(r"\.csv$",".html",csv_file)
    if csv_file == html_file:
        continue
    write_standard_html_file(html_file,map_list)

