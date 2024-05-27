
import struct

from apodlib.docImage import *

class MSWINFNT:
    class charReturn:
        bmp = None
        width = None
        height = None
        stride = None
    class headerStruct:
        class charTableEntry:
            charWidth = None
            charOffset = None
            charPixelOffset = 0
        # The documentation here is junk [https://jeffpar.github.io/kbarchive/kb/065/Q65123/]
        # It does not list offsets, it fails to list sizes for some fields, and it lists fields
        # without mentioning which version they belong to without mentioning that nothing exists
        # past dfReserved for version 0x200 (the dfCharTable follows immediately after that).
        fmt = "<HL60sHHHHHHHBBBHBHHBHHBBBBHLLLLB"
        fmtsz = struct.calcsize(fmt)
        dfVersion = None
        dfSize = None
        dfCopyright = None
        dfType = None
        dfPoints = None
        dfVertRes = None
        dfHorizRes = None
        dfAscent = None
        dfInternalLeading = None
        dfExternalLeading = None
        dfItalic = None
        dfUnderline = None
        dfStrikeOut = None
        dfWeight = None
        dfCharSet = None
        dfPixWidth = None
        dfPixHeight = None
        dfPitchAndFamily = None
        dfAvgWidth = None
        dfMaxWidth = None
        dfFirstChar = None
        dfLastChar = None
        dfDefaultChar = None
        dfBreakChar = None
        dfWidthBytes = None
        dfDevice = None
        dfFace = None
        dfBitsPointer = None
        dfBitsOffset = None
        dfReserved = None
        dfCharTableOffset = None
        dfCharTable = None
        #
        def parse(self,raw):
            self.dfVersion,self.dfSize,self.dfCopyright,self.dfType,self.dfPoints,self.dfVertRes,self.dfHorizRes,self.dfAscent,self.dfInternalLeading,self.dfExternalLeading,self.dfItalic,self.dfUnderline,self.dfStrikeOut,self.dfWeight,self.dfCharSet,self.dfPixWidth,self.dfPixHeight,self.dfPitchAndFamily,self.dfAvgWidth,self.dfMaxWidth,self.dfFirstChar,self.dfLastChar,self.dfDefaultChar,self.dfBreakChar,self.dfWidthBytes,self.dfDevice,self.dfFace,self.dfBitsPointer,self.dfBitsOffset,self.dfReserved = struct.unpack(self.fmt,raw[0:self.fmtsz])
            if self.dfVersion < 0x100 or self.dfVersion > 0x3FF or self.dfSize > len(raw) or self.dfFirstChar > self.dfLastChar:
                raise Exception("windows fnt header error")
            # Fuck, figure out the offset despite the mediocre documentation URL listed above
            if self.dfVersion >= 0x300:
                self.dfCharTableOffset = 0x94; # FIXME: Untested
            elif self.dfVersion >= 0x200:
                self.dfCharTableOffset = 0x76;
            else:
                self.dfCharTableOffset = 0x77; # Windows 1.0 actually reserves 0x76 for a flags field which is always zero
            # We do not support vector FNT files (that means you, Windows 1.0 ROMAN.FON)
            if not (self.dfType & 1) == 0:
                raise Exception("windows vector fnt files not supported")
            #
            if self.dfVersion >= 0x200:
                charTableEntries = self.dfLastChar + 2 - self.dfFirstChar
            else:
                charTableEntries = self.dfLastChar + 1 - self.dfFirstChar
            #
            self.dfCharTable = [ None ] * charTableEntries
            if self.dfVersion >= 0x300:
                for i in range(0,charTableEntries):
                    ent = self.charTableEntry()
                    blobofs = self.dfCharTableOffset+(i*6)
                    blob = raw[blobofs:blobofs+6]
                    ent.charWidth,ent.charOffset = struct.unpack("<HL",blob)
                    self.dfCharTable[i] = ent
            elif self.dfVersion >= 0x200:
                for i in range(0,charTableEntries):
                    ent = self.charTableEntry()
                    blobofs = self.dfCharTableOffset+(i*4)
                    blob = raw[blobofs:blobofs+4]
                    ent.charWidth,ent.charOffset = struct.unpack("<HH",blob)
                    self.dfCharTable[i] = ent
            elif self.dfPixWidth > 0: # fixed width fonts, Windows 1.0
                for i in range(0,charTableEntries):
                    cX = self.dfPixWidth * i
                    ent = self.charTableEntry()
                    ent.charWidth = self.dfPixWidth
                    ent.charOffset = (cX >> 3) + self.dfBitsOffset
                    ent.charPixelOffset = cX & 7
                    self.dfCharTable[i] = ent
            else: # variable width fonts, Windows 1.0
                # Windows 1.0 bitmap fonts could be thought of as one large horizontal strip of font height
                # containing all the characters, with a list of 16-bit integers listing the ending X coordinate
                # of each one in ascending order. Which means to get the width of each one, read the value and
                # subtract from it the previous X coordinate.
                #
                # There are Windows 1.0 fonts that use the 2.0 table like format of charWidth and charOffset
                # but charOffset is relative to dfBitsOffset and it's only ever used for vector FNT files like
                # ROMAN.FON.
                #
                # If the font is fixed width according to the header, then the charTableEntries do not exist
                # in the file.
                if self.dfWidthBytes == 0 or self.dfPixHeight == 0:
                    raise Exception("Windows 1.0 FNT error: width in bytes and height not specified")
                #
                pX = 0
                for i in range(0,charTableEntries):
                    ent = self.charTableEntry()
                    blobofs = self.dfCharTableOffset+(i*2)
                    blob = raw[blobofs:blobofs+2]
                    cX = struct.unpack("<H",blob)[0]
                    if cX < pX:
                        raise Exception("Windows 1.0 FNT error: X coordinates are not in ascending order at i="+str(i)+"/"+str(charTableEntries))
                    if cX > (self.dfWidthBytes*8):
                        raise Exception("Windows 1.0 FNT error: X coordinate > bitmap width")
                    ent.charWidth = cX - pX
                    ent.charOffset = (pX >> 3) + self.dfBitsOffset
                    ent.charPixelOffset = pX & 7
                    self.dfCharTable[i] = ent
                    pX = cX
        #
        def __str__(self):
            return "[MSWINFNT dfVersion="+hex(self.dfVersion)+" dfCopyright="+str(self.dfCopyright)+" dfType="+str(self.dfType)+" dfPoints="+str(self.dfPoints)+" dfAscent="+str(self.dfAscent)+" dfInternalLeading="+str(self.dfInternalLeading)+" dfExternalLeading="+str(self.dfExternalLeading)+" dfCharSet="+str(self.dfCharSet)+" dfPixWidth="+str(self.dfPixWidth)+" dfPixHeight="+str(self.dfPixHeight)+" dfPitchAndFamily="+hex(self.dfPitchAndFamily)+" dfMaxWidth="+str(self.dfMaxWidth)+" dfFirstChar="+str(self.dfFirstChar)+" dfLastChar="+str(self.dfLastChar)+" dfDefaultChar="+str(self.dfDefaultChar)+" dfWidthBytes="+str(self.dfWidthBytes)+" dfBitsOffset="+str(self.dfBitsOffset)+" dfCharTableOffset="+str(self.dfCharTableOffset)+"]"
        def __init__(self,raw):
            self.parse(raw)
    #
    fntraw = None
    header = None
    def parse(self,fntraw):
        self.header = self.headerStruct(fntraw)
    def __init__(self,*,path=None,raw=None):
        if not path == None:
            f = open(path,mode="rb")
            self.fntraw = f.read()
            f.close()
        elif not raw == None:
            self.fntraw = raw
        else:
            raise Exception("Nothing given")
        #
        self.parse(self.fntraw)
    def getchar(self,c,*,genDocImage=False):
        if type(c) == str:
            if len(c) > 1:
                raise Exception("Only one char allowed")
            c = ord(c[0])
        #
        idx = self.header.dfDefaultChar
        if c >= self.header.dfFirstChar and c <= self.header.dfLastChar:
            idx = c - self.header.dfFirstChar
        #
        r = self.charReturn()
        sent = self.header.dfCharTable[idx]
        r.width = sent.charWidth
        r.height = self.header.dfPixHeight
        bmpo = sent.charOffset
        if self.header.dfVersion >= 0x200:
            r.stride = int((r.width+7)/8)
            r.bmp = self.fntraw[bmpo:bmpo+(r.height*r.stride)]
        else:
            r.stride = int((r.width+15)/8) & (~1) # word align
            r.bmp = self.fntraw[bmpo:bmpo+(r.height*self.header.dfWidthBytes)]
        #
        if genDocImage == True:
            if self.header.dfVersion >= 0x200:
                # OK, so get this: Microsoft raster fonts are stored as vertical strips. They are not bitmaps like you are accustomed to.
                # That means for a 9-pixel wide "B" for example, the left 8 pixels are sent, then the right 8 pixels.
                r.docImage = docImage(r.width,r.height,1)
                for col in range(0,r.stride):
                    for row in range(0,r.height):
                        r.docImage.rows[row][col] = r.bmp[(col*r.height)+row]
            else:
                # Windows 1.0 bitmap fonts are like a really wide bitmap containing all characters, and the table gives us the X coordinates of each
                r.docImage = docImage(r.width,r.height,1)
                for col in range(0,r.stride):
                    if sent.charPixelOffset == 0:
                        for row in range(0,r.height):
                            try:
                                r.docImage.rows[row][col] = r.bmp[(row*self.header.dfWidthBytes)+col]
                            except:
                                True
                    else:
                        for row in range(0,r.height):
                            try:
                                r.docImage.rows[row][col] = ((r.bmp[(row*self.header.dfWidthBytes)+col] << sent.charPixelOffset) | (r.bmp[(row*self.header.dfWidthBytes)+col+1] >> (8-sent.charPixelOffset))) & 0xFF
                            except:
                                True
        #
        return r
    def getWidestOfChar(self,s):
        w = 0
        for cc in s:
            nfo = self.getchar(ord(cc))
            if w < nfo.width:
                w = nfo.width
        return w

