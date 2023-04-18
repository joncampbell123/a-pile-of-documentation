#!/usr/bin/python3

import re
import sys
import csv
import math

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
        bv += bytearray([4])
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

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
f = open("gen-ascii.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Code (hexadecimal)',      'Code (decimal)',          'Code (octal)',            'Code (binary)',          'Unicode code point','name',  'description','display',         '#column-names'])
csw.writerow(['numeric:base=16,multiple','numeric:base=10,multiple','numeric:base=10,multiple','numeric:base=2,multiple','numeric:base=16',   'string','string',     'string/image',    '#column-format'])
csw.writerow(['right',                   'right',                   'right',                   'right',                  'right',             'left',  'left',       'left',            '#column-align'])
csw.writerow(['ASCII table',                                                                                                                           '#table-title'])
csw.writerow([])
for i in range(0,128): # the first 128 of CP437 is the same as ASCII
    ent = map_cp437[i]
    vhex = ent.getHexString()
    vdec = ent.getDecString()
    voct = ent.getOctString()
    vbin = ent.getBinString()
    unicp_s = ent.getUnicpString()
    disp_s = ent.getDisplayString()
    csw.writerow([vhex,vdec,voct,vbin,unicp_s,ent.name,'',disp_s])
f.close()

