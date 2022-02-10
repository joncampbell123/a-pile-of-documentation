
import os
import glob
import json
import zlib
import struct
import pathlib

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

