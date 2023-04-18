#!/usr/bin/python3

import re
import sys
import csv
import math

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
        [ 0x1F, 0x25BC ]  # triangle arrow down
]

# cp932
cp932_control_codes = [
        # byte value, unicode point
        [ 0x5C, 0x00A5 ], # yen
        [ 0x7E, 0x203E ]  # overline
]

def patch_cp437_control_codes(m):
    # CP437 has well known symbols in the range 0-31 inclusive which
    # this code will patch in now.
    global cp437_control_codes
    for ent in cp437_control_codes:
        m[ent[0]].unicp = ent[1]
        if not ent[1] == None:
            m[ent[0]].display = chr(ent[1])

def patch_shiftjis_replaced_ascii_codes(m):
    # Unicode list forgot to list that backslash was replaced by Yen (which is why
    # Japanese systems have such strange looking DOS prompts) and tilde by a
    # top horizontal line.
    global cp932_control_codes
    for ent in cp932_control_codes:
        m[ent[0]].unicp = ent[1]
        if not ent[1] == None:
            m[ent[0]].display = chr(ent[1])

class UnicodeMapEntry:
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
        if self.unicp == None:
            return '    '
        unicp_s = hex(self.unicp)[2:]
        while len(unicp_s) < 4:
            unicp_s = '0' + unicp_s
        return unicp_s
    def getDisplayString(self):
        disp = ''
        if not ent.display == None:
            disp = ent.display
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
        name = t1[1]
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
        if not unicp[0:2] == "0x":
            continue
        unicp = int(unicp[2:],16)
        #
        ent = UnicodeMapEntry()
        ent.byteseq = bv
        ent.unicp = unicp
        ent.name = name
        ent.display = None
        if ent.unicp >= 32 and not ent.unicp == 127:
            ent.display = chr(ent.unicp)
        ret[key] = ent
        #
    f.close()
    return ret

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

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
f = open("gen-ascii.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['ASCII table', '#table-title'])
csw.writerow([])
for enti in map_ascii:
    ent = map_ascii[enti]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
f = open("gen-cp437.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['Microsoft/IBM PC Code Page 437 table (Latin US)', '#table-title'])
csw.writerow([])
for enti in map_cp437:
    ent = map_cp437[enti]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
map_current = load_unicode_mapping_file("ref/CP737.TXT")
patch_cp437_control_codes(map_current)
f = open("gen-cp737.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['Microsoft/IBM PC Code Page 737 table (Greek)', '#table-title'])
csw.writerow([])
for enti in map_current:
    ent = map_current[enti]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
map_current = load_unicode_mapping_file("ref/CP1252.TXT")
f = open("gen-cp1252.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['Microsoft Windows Code Page 1252 (Latin ISO 8859-1)', '#table-title'])
csw.writerow([])
for enti in map_current:
    ent = map_current[enti]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
map_current = load_unicode_mapping_file("ref/CP932.TXT")
patch_shiftjis_replaced_ascii_codes(map_current)
f = open("gen-cp932.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['Microsoft/IBM PC Code Page 932 table (Shift JIS)', '#table-title'])
csw.writerow([])
for enti in map_current:
    ent = map_current[enti]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

