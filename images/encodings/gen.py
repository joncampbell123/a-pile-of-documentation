#!/usr/bin/python3

import re
import sys
import csv
import math
import struct

# typedef struct tagBITMAPFILEHEADER {
#   WORD  bfType;
#   DWORD bfSize;
#   WORD  bfReserved1;
#   WORD  bfReserved2;
#   DWORD bfOffBits;
# } BITMAPFILEHEADER, *LPBITMAPFILEHEADER, *PBITMAPFILEHEADER;
class BITMAPFILEHEADER:
    fmt = "<HLHHL"
    fmtsz = struct.calcsize(fmt)
    bfType = None
    bfSize = None
    bfReserved1 = 0
    bfReserved2 = 0
    bfOffBits = None
    def __init__(self,d=None):
        if not d == None:
            self.decode(d)
    def decode(self,d):
        self.bfType,self.bfSize,self.bfReserved1,self.bfReserved2,self.bfOffBits = struct.unpack(self.fmt,d[0:self.fmtsz])
    def encode(self):
        return struct.pack(self.fmt,self.bfType,self.bfSize,self.bfReserved1,self.bfReserved2,self.bfOffBits)
    def __str__(self):
        return "[BITMAPFILEHEADER bfType="+hex(self.bfType)+" bfSize="+str(self.bfSize)+" bfOffBits="+str(self.bfOffBits)+"]"

# typedef struct tagBITMAPINFOHEADER {
#   DWORD biSize;
#   LONG  biWidth;
#   LONG  biHeight;
#   WORD  biPlanes;
#   WORD  biBitCount;
#   DWORD biCompression;
#   DWORD biSizeImage;
#   LONG  biXPelsPerMeter;
#   LONG  biYPelsPerMeter;
#   DWORD biClrUsed;
#   DWORD biClrImportant;
# } BITMAPINFOHEADER, *LPBITMAPINFOHEADER, *PBITMAPINFOHEADER;
class BITMAPINFOHEADER:
    fmt = "<LllHHLLllLL"
    fmtsz = struct.calcsize(fmt)
    biSize = None
    biWidth = None
    biHeight = None
    biPlanes = None
    biBitCount = None
    biCompression = None
    biSizeImage = None
    biXPelsPerMeter = 0
    biYPelsPerMeter = 0
    biClrUsed = 0
    biClrImportant = 0
    def __init__(self,d=None):
        if not d == None:
            self.decode(d)
    def decode(self,d):
        self.biSize = struct.unpack("<L",d[0:4])[0]
        # TODO: BITMAPINFOHEADERV4, BITMAPINFOHEADERV5, which you can distinguish using biSize
        if self.biSize >= 512:
            raise Exception("BITMAPINFOHEADER unknown biSize="+str(self.biSize))
        elif self.biSize >= 40:
            self.biSize,self.biWidth,self.biHeight,self.biPlanes,self.biBitCount,self.biCompression,self.biSizeImage,self.biXPelsPerMeter,self.biYPelsPerMeter,self.biClrUsed,self.biClrImportant = struct.unpack(self.fmt,d[0:self.fmtsz])
        else:
            raise Exception("BITMAPINFOHEADER unknown biSize="+str(self.biSize))
    def encode(self):
        if self.biSize == 40:
            return struct.pack(self.fmt,self.biSize,self.biWidth,self.biHeight,self.biPlanes,self.biBitCount,self.biCompression,self.biSizeImage,self.biXPelsPerMeter,self.biYPelsPerMeter,self.biClrUsed,self.biClrImportant)
        else:
            raise Exception("BITMAPINFOHEADER unknown biSize="+str(self.biSize))
    def __str__(self):
        return "[BITMAPINFOHEADER biSize="+hex(self.biSize)+" biWidth="+str(self.biWidth)+" biHeight="+str(self.biHeight)+" biPlanes="+str(self.biPlanes)+" biBitCount="+str(self.biBitCount)+" biCompression="+hex(self.biCompression)+" biSizeImage="+str(self.biSizeImage)+" biClrUsed="+str(self.biClrUsed)+" biClrImportant="+str(self.biClrImportant)+"]"

class docRGBA:
    R = None
    G = None
    B = None
    A = None
    def __init__(self,r=None,g=None,b=None,a=None):
        self.R = r
        self.G = g
        self.B = b
        self.A = a

class docImage:
    rows = None # array of bytearray containing pixels
    width = None
    height = None
    stride = None
    maprow = None
    palette = None # array of docRGBA
    bits_per_pixel = None
    bytes_per_pixel = None
    readpixelp = None
    writepixelp = None
    def __init__(self,w,h,bpp,*,initBMP=None,initBMPStride=None):
        self.width = w
        self.height = h
        self.bits_per_pixel = bpp
        if not (bpp == 1 or bpp == 4 or bpp == 8 or bpp == 15 or bpp == 16 or bpp == 24 or bpp == 32):
            raise Exception("wrong bit depth docImage init bpp="+str(bpp))
        if self.bits_per_pixel >= 8:
            self.bytes_per_pixel = int((self.bits_per_pixel+7)/8)
            self.stride = self.bytes_per_pixel * int((self.width + 3) & (~3))
        else:
            self.bytes_per_pixel = 0
            self.stride = int(((self.bits_per_pixel * self.width)+7)/8)
        if self.bits_per_pixel >= 1 and self.bits_per_pixel <= 8:
            self.palette_used = 1 << self.bits_per_pixel
            self.palette = [ None ] * (1 << self.bits_per_pixel)
            for i in range(0,len(self.palette)):
                self.palette[i] = docRGBA(0,0,0,0)
        if not initBMP == None:
            self.maprow = self.def_maprow_bmp
            if not initBMPStride == None:
                self.stride = initBMPStride
            self.rows = [ initBMP ]
        else:
            self.maprow = self.def_maprow
            self.rows = [ 0 ] * self.height
            for i in range(0,self.height):
                self.rows[i] = bytearray(self.stride)
        #
        if bpp == 1:
            self.readpixelp = self.readpixel_1
            self.writepixelp = self.writepixel_1
        elif bpp == 4:
            self.readpixelp = self.readpixel_4
            self.writepixelp = self.writepixel_4
        elif bpp == 8:
            self.readpixelp = self.readpixel_8
            self.writepixelp = self.writepixel_8
        elif bpp == 15:
            self.readpixelp = self.readpixel_15
            self.writepixelp = self.writepixel_15
        elif bpp == 16:
            self.readpixelp = self.readpixel_16
            self.writepixelp = self.writepixel_16
        elif bpp == 24:
            self.readpixelp = self.readpixel_24
            self.writepixelp = self.writepixel_24
        elif bpp == 32:
            self.readpixelp = self.readpixel_32
            self.writepixelp = self.writepixel_32
    def def_maprow(self,y):
        if y >= 0 and y < len(self.rows):
            return self.rows[y]
        return bytearray(self.stride)
    def def_maprow_bmp(self,y):
        if y >= 0 and y < self.height:
            return self.rows[0][y*self.stride:(y+1):self.stride]
        return bytearray(self.stride)
    def readpixel(self,x,y):
        return self.readpixelp(self.maprow(y),x)
    def writepixel(self,x,y,c):
        self.writepixelp(self.maprow(y),x,c)
    def readpixel_1(self,rp,x):
        byo = x >> 3
        bio = x & 7
        if byo < len(rp):
            return (rp[byo] >> (7-bio)) & 0x1
        return 0
    def readpixel_4(self,rp,x):
        return 0
    def readpixel_8(self,rp,x):
        if x < len(rp):
            return rp[x]
        return 0
    def readpixel_15(self,rp,x):
        return 0
    def readpixel_16(self,rp,x):
        return 0
    def readpixel_24(self,rp,x):
        return 0
    def readpixel_32(self,rp,x):
        return 0
    def writepixel_1(self,rp,x,c):
        byo = x >> 3
        bio = x & 7
        if byo < len(rp):
            rp[byo] &= ~(0x80 >> bio)
            rp[byo] |= (c&0x1) << (7-bio)
    def writepixel_4(self,rp,x,c):
        True
    def writepixel_8(self,rp,x,c):
        if x < len(rp):
            rp[x] = c&0xFF
    def writepixel_15(self,rp,x,c):
        True
    def writepixel_16(self,rp,x,c):
        True
    def writepixel_24(self,rp,x,c):
        True
    def writepixel_32(self,rp,x,c):
        True
    def __str__(self):
        return "[docImage width="+str(self.width)+" height="+str(self.height)+" stride="+str(self.stride)+" bits/pixel="+str(self.bits_per_pixel)+" bytes/pixel="+str(self.bytes_per_pixel)+"]"
    def fillrect(self,x1,y1,x2,y2,c):
        for y in range(y1,y2):
            for x in range(x1,x2):
                self.writepixel(x,y,c)

def docLoadBMPUncompressed(fileinfo,bmpinfo,bmp):
    if bmpinfo.biWidth < 0 or bmpinfo.biHeight < 0:
        raise Exception("BMP format with negative w/h values not supported")
    if bmpinfo.biWidth > 0 and not bmpinfo.biHeight == 0 and bmpinfo.biPlanes == 1:
        dibBits = bmp[fileinfo.bfOffBits:fileinfo.bfOffBits+bmpinfo.biSizeImage]
        img = docImage(bmpinfo.biWidth,bmpinfo.biHeight,bmpinfo.biBitCount)
        if not img.palette == None and bmpinfo.biBitCount <= 8:
            clr = len(img.palette)
            if clr > bmpinfo.biClrUsed:
                clr = bmpinfo.biClrUsed
            img.palette_used = clr
            # BMP palette follows BITMAPINFOHEADER BGRA (or, well, it's really just RGBX)
            palBytes = bmp[14+bmpinfo.biSize:14+bmpinfo.biSize+(4*clr)]
            for i in range(0,clr):
                palEnt = palBytes[i*4:(i+1)*4]
                img.palette[i].B = palEnt[0]
                img.palette[i].G = palEnt[1]
                img.palette[i].R = palEnt[2]
                img.palette[i].A = 0xFF
        bmpStride = (((bmpinfo.biWidth * bmpinfo.biBitCount) + 31) & (~31)) >> 3
        cpyStride = bmpStride
        if cpyStride > img.stride:
            cpyStride = img.stride
        # bitmaps are "upside down"
        for py in range(0,bmpinfo.biHeight):
            ny = bmpinfo.biHeight - (1 + py)
            row = img.rows[ny]
            row[0:cpyStride] = dibBits[bmpStride*py:(bmpStride*py)+cpyStride]
        #
        return img
    raise Exception("Unknown BMP format")

def docLoadBMP(bmp):
    if isinstance(bmp,bytearray) or isinstance(bmp,bytes):
        fileinfo = BITMAPFILEHEADER(bmp)
        if not fileinfo.bfType == 0x4d42 or fileinfo.bfOffBits == 0:
            raise Exception("Not a BMP file")
        bmpinfo = BITMAPINFOHEADER(bmp[14:])
        if bmpinfo.biCompression == 0:
            return docLoadBMPUncompressed(fileinfo,bmpinfo,bmp)
        raise Exception("Unknown BMP compression")
    elif type(bmp) == str:
        f = open(bmp,mode="rb")
        bmp = f.read()
        f.close()
        return docLoadBMP(bmp)
    raise Exception("docLoadBMP unhandled type "+str(type(bmp)))

def docWriteBMP(dst,img):
    totsz = BITMAPFILEHEADER.fmtsz + 40
    #
    palsz = 0
    palOff = totsz
    if not img.palette == None:
        palsz = len(img.palette)
        if palsz > img.palette_used:
            palsz = img.palette_used
        totsz += palsz * 4
    #
    dibOff = totsz
    #
    bmpStride = (((img.width * img.bits_per_pixel) + 31) & (~31)) >> 3
    dibSize = bmpStride * img.height
    totsz += dibSize
    #
    cpyStride = bmpStride
    if cpyStride > img.stride:
        cpyStride = img.stride
    #
    raw = bytearray(totsz)
    #
    fileinfo = BITMAPFILEHEADER()
    fileinfo.bfType = 0x4d42
    fileinfo.bfSize = totsz
    fileinfo.bfOffBits = dibOff
    raw[0:14] = fileinfo.encode()
    #
    bmpinfo = BITMAPINFOHEADER()
    bmpinfo.biSize = 40
    bmpinfo.biWidth = img.width
    bmpinfo.biHeight = img.height
    bmpinfo.biPlanes = 1
    bmpinfo.biBitCount = img.bits_per_pixel
    bmpinfo.biCompression = 0
    bmpinfo.biSizeImage = dibSize
    bmpinfo.biXPelsPerMeter = 0
    bmpinfo.biYPelsPerMeter = 0
    bmpinfo.biClrUsed = palsz
    bmpinfo.biClrImportant = palsz
    raw[14:14+40] = bmpinfo.encode()
    #
    if palsz > 0:
        for pi in range(0,len(img.palette)):
            raw[palOff+(pi*4)+0] = img.palette[pi].B
            raw[palOff+(pi*4)+1] = img.palette[pi].G
            raw[palOff+(pi*4)+2] = img.palette[pi].R
            raw[palOff+(pi*4)+3] = 0
    #
    for py in range(0,img.height):
        ny = img.height - (1 + py)
        raw[dibOff+(ny*bmpStride):dibOff+(ny*bmpStride)+cpyStride] = img.rows[py][0:cpyStride]
    #
    if type(dst) == str:
        f = open(dst,mode="wb")
        f.write(raw)
        f.close()
    elif dst == None:
        True
    else:
        raise Exception("Asked to encode BMP to unknown type")
    #
    return raw

def docImageStackCombine(imgs):
    final_h = 0
    final_w = 0
    for simg in imgs:
        final_h += simg.height
        if final_w < simg.width:
            final_w = simg.width
    #
    img = docImage(final_w,final_h,imgs[0].bits_per_pixel)
    img.palette = imgs[0].palette
    img.palette_used = imgs[0].palette_used
    #
    y = 0
    for simg in imgs:
        h = simg.height
        img.rows[y:y+h] = simg.rows[0:h]
        y += h
    #
    return img

def imgmonocopy(dimg,dx,dy,w,h,simg,sx,sy,lf):
    for y in range(0,h):
        for x in range(0,w):
            dimg.writepixel(dx+x,dy+y,lf(simg.readpixel(sx+x,sy+y)))

def drawchargrid(*,imgt8=None,tcWidth=None,tcHeight=None,colDigits=2,imgcp,charCols=16,charRows=16,charCellWidth=8,charCellHeight=16,code_base=0,charCellSizeLF=None,gridMapFunc=None,textMapFunc=None):
    if imgt8 == None:
        imgt8 = imgcp
    if tcWidth == None:
        tcWidth = charCellWidth
    if tcHeight == None:
        tcHeight = charCellHeight
    if charCellSizeLF == None:
        charCellSizeLF = lambda c,w,h: [w,h]
    if gridMapFunc == None:
        gridMapFunc = lambda c: [(c&0xF)*charCellWidth,(c>>4)*charCellHeight]
    if textMapFunc == None:
        textMapFunc = lambda c: [(c&0xF)*tcWidth,(c>>4)*tcHeight]
    #
    charGridX = 1+(tcWidth*colDigits)
    charGridY = 1+tcHeight
    img = docImage(((charCellWidth+1)*charCols)+charGridX,((charCellHeight+1)*charRows)+charGridY,8)
    #
    img.palette_used = 3
    img.palette[0] = docRGBA(0,0,0,0)
    img.palette[1] = docRGBA(255,255,255,255)
    img.palette[2] = docRGBA(63,63,192)
    #
    img.fillrect(0,0,img.width,img.height,1)
    img.fillrect(charGridX-1,charGridY-1,img.width,img.height,2)
    #
    for c in range(0,charCols):
        s = hex(c)[2:].upper()
        sx,sy = textMapFunc(ord(s[0]))
        dx = charGridX + (c * (charCellWidth+1)) + int(max(0,charCellWidth-tcWidth) / 2)
        dy = 0
        imgmonocopy(img,dx,dy,tcWidth,tcHeight,imgt8,sx,sy,lambda _x: (_x ^ 1))
    #
    for r in range(0,charRows):
        code = hex(code_base + (r<<4))[2:].upper()
        while len(code) < colDigits:
            code = '0' + code
        #
        dy = charGridY + (r * (charCellHeight+1)) + int(max(0,charCellHeight-tcHeight) / 2)
        #
        for ci in range(0,colDigits):
            dx = tcWidth*ci
            sx,sy = textMapFunc(ord(code[ci]))
            imgmonocopy(img,dx,dy,tcWidth,tcHeight,imgt8,sx,sy,lambda _x: (_x ^ 1))
    #
    for r in range(0,charRows):
        for c in range(0,charCols):
            charcode = code_base + (r * 16) + c
            dx = charGridX + (c * (charCellWidth+1))
            dy = charGridY + (r * (charCellHeight+1))
            cw,ch = charCellSizeLF(charcode,charCellWidth,charCellHeight)
            if cw > 0 and ch > 0:
                sx,sy = gridMapFunc((r<<4)+c)
                imgmonocopy(img,dx,dy,cw,ch,imgcp,sx,sy,lambda _x: _x)
    #
    return img

#-----------------------------------------------------
docWriteBMP("gen-cp437.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp437vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp850.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp850vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp851.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp851vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp852.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp852vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp853.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp853vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp855.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp855vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp857.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp857vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp862.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp862vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp864.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp864vga8x16.bmp")))

#-----------------------------------------------------
docWriteBMP("gen-cp866.bmp",drawchargrid(imgcp=docLoadBMP("ref/cp866vga8x16.bmp")))

#-----------------------------------------------------
pc98rom = None
PC98FONT = None
img_pc98sbcs = None
img_pc98dbcs = None

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
            if self.dfVersion < 0x200 or self.dfVersion > 0x3FF or self.dfSize > len(raw) or self.dfFirstChar > self.dfLastChar:
                raise Exception("windows fnt header error")
            # Fuck, figure out the offset despite the mediocre documentation URL listed above
            if self.dfVersion >= 0x300:
                self.dfCharTableOffset = 0x94; # FIXME: Untested
            else:
                self.dfCharTableOffset = 0x76;
            #
            charTableEntries = self.dfLastChar + 2 - self.dfFirstChar
            self.dfCharTable = [ None ] * charTableEntries
            if self.dfVersion >= 0x300:
                for i in range(0,charTableEntries):
                    ent = self.charTableEntry()
                    blobofs = self.dfCharTableOffset+(i*4)
                    blob = raw[blobofs:blobofs+4]
                    ent.charWidth,ent.charOffset = struct.unpack("<HL",blob)
                    self.dfCharTable[i] = ent
            else:
                for i in range(0,charTableEntries):
                    ent = self.charTableEntry()
                    blobofs = self.dfCharTableOffset+(i*4)
                    blob = raw[blobofs:blobofs+4]
                    ent.charWidth,ent.charOffset = struct.unpack("<HH",blob)
                    self.dfCharTable[i] = ent
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
    def __init__(self,path):
        f = open(path,mode="rb")
        self.fntraw = f.read()
        f.close()
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
        r.stride = int((r.width+7)/8)
        bmpo = sent.charOffset
        r.bmp = self.fntraw[bmpo:bmpo+(r.height*r.stride)]
        #
        if genDocImage == True:
            # OK, so get this: Microsoft raster fonts are stored as vertical strips. They are not bitmaps like you are accustomed to.
            # That means for a 9-pixel wide "B" for example, the left 8 pixels are sent, then the right 8 pixels.
            r.docImage = docImage(r.width,r.height,1)
            for col in range(0,r.stride):
                for row in range(0,r.height):
                    r.docImage.rows[row][col] = r.bmp[(col*r.height)+row]
        #
        return r
    def getWidestOfChar(self,s):
        w = 0
        for cc in s:
            nfo = self.getchar(ord(cc))
            if w < nfo.width:
                w = nfo.width
        return w

# Windows code page 1252, System font extracted from Windows 3.1
win31sysfnt = MSWINFNT("ref/window31_system_font_cp1252.fnt")
wgridw = win31sysfnt.header.dfMaxWidth
wgridh = win31sysfnt.header.dfPixHeight
wgrid = docImage(wgridw*16,wgridh*16,1)
wgrid.fillrect(0,0,wgrid.width,wgrid.height,0)
textw = win31sysfnt.getWidestOfChar('0123456789ABCDEF')
for r in range(0,16):
    for c in range(0,16):
        cc = (r << 4) + c
        wbmpinfo = win31sysfnt.getchar(cc,genDocImage=True)
        imgmonocopy(wgrid,c*wgridw,r*wgridh,wbmpinfo.width,wbmpinfo.height,wbmpinfo.docImage,0,0,lambda _x: _x)
#
docWriteBMP("gen-windows31-cp1252-system.bmp",drawchargrid(tcWidth=textw,textMapFunc=lambda cc: [(cc&0xF)*wgridw,(cc>>4)*wgridh],imgcp=wgrid,charCellWidth=wgridw,charCellHeight=wgridh))
win31sysfnt = None
wbmpinfo = None
wgrid = None

# Windows code page 1252, Fixedsys font extracted from Windows 3.1
win31sysfnt = MSWINFNT("ref/window31_fixedsys_font_cp1252.fnt")
wgridw = win31sysfnt.header.dfMaxWidth
wgridh = win31sysfnt.header.dfPixHeight
wgrid = docImage(wgridw*16,wgridh*16,1)
wgrid.fillrect(0,0,wgrid.width,wgrid.height,0)
textw = win31sysfnt.getWidestOfChar('0123456789ABCDEF')
for r in range(0,16):
    for c in range(0,16):
        cc = (r << 4) + c
        wbmpinfo = win31sysfnt.getchar(cc,genDocImage=True)
        imgmonocopy(wgrid,c*wgridw,r*wgridh,wbmpinfo.width,wbmpinfo.height,wbmpinfo.docImage,0,0,lambda _x: _x)
#
docWriteBMP("gen-windows31-cp1252-fixedsys.bmp",drawchargrid(tcWidth=textw,textMapFunc=lambda cc: [(cc&0xF)*wgridw,(cc>>4)*wgridh],imgcp=wgrid,charCellWidth=wgridw,charCellHeight=wgridh))
win31sysfnt = None
wbmpinfo = None
wgrid = None

#-----------------------------------------------------
# PC-98 FONT ROM, video memory text codes
# at 0x00000 = 8x8 single wide 8-bit character cells (not used here)
# at 0x00800 = 8x16 single wide 8-bit character cells
# at 0x01800 = 96x92 double wide character cells
class PC98FONTROM:
    ROM = None
    def font8x8(self):
        return self.ROM[0:8*256]
    def char8x8(self,c):
        o = c*8
        return self.font8x8()[o:o+8]
    def font8x16(self):
        return self.ROM[0x800:0x800+(16*256)]
    def char8x16(self,c):
        o = c*16
        return self.font8x16()[o:o+16]
    def font16x16(self):
        return self.ROM[0x1800:0x1800+(16*2*96*92)] # 16x16 96x92 grid
    def char16x16(self,c):
        h = ((c >> 8) & 0x7F) - 0x20
        l = c & 0x7F
        if h < 0 or h > 95 or l <= 0 or l > 92:
            return [ 0 ] * 16 * 2
        o = ((l-1) * 96 * 16 * 2) + (h * 16 * 2)
        return self.font16x16()[o:o+(16*2)]
    def __init__(self,path="ref/pc98font.rom"):
        f = open(path,mode="rb")
        self.ROM = f.read()
        f.close()

#-----------------------------------------------------
PC98FONT = PC98FONTROM()

def PC98IsSJIS(cc):
    if (cc >= 0x8100 and cc <= 0x9F00) or (cc >= 0xE000 and cc <= 0xEF00):
        b = cc & 0xFF
        if b >= 0x40 and not b == 0x7F:
            return True
    return False

def PC98NotSJISCellSize(cc,w,h):
    if (cc >= 0x8100 and cc <= 0x9FFF) or (cc >= 0xE000 and cc <= 0xEFFF):
        return [0,0]
    return [w,h]

def PC98SJISCellSize(cc,w,h):
    if PC98IsSJIS(cc):
        if cc >= 0x8540 and cc < 0x8690:# half width special NEC chars
            return [8,h]
        return [w,h]
    return [0,0]

def DecodeSJIS(h,l):
    if h >= 0x81 and h <= 0x9F:
        b1 = (h - 112) * 2
    elif h >= 0xE0 and h <= 0xEF:
        b1 = (h - 176) * 2
    else:
        return [-1,-1]

    if l >= 0x9F:
        b2 = l - 126
    elif l == 0x7F:
        return [-1,-1]
    elif l >= 0x40:
        b1 -= 1
        b2 = l - 31
        if l >= 0x80:
            b2 -= 1

    return [b1,b2]

# despite the normally double wide cells, there is a small range where the double wide encoding becomes a single wide char.
# these are apparently special nonstandard codes defined by NEC.
def PC98dbcsCellLambda(cc,w,h):
    if (cc & 0xFC) == 0x08: # xx08 xx09 xx0A xx0B
        return [8,h]
    #
    return [w,h]

#-----------------------------------------------------
# PC-98 sbcs
img_pc98sbcs = docImage(8,16*256,1,initBMP=PC98FONT.font8x16(),initBMPStride=1)
docWriteBMP("gen-pc98-tvram-0000.bmp",drawchargrid(colDigits=4,imgcp=img_pc98sbcs,textMapFunc=lambda cc: [0,cc*16],gridMapFunc=lambda cc: [0,cc*16]))
docWriteBMP("gen-pc98-sjis-0000.bmp",drawchargrid(colDigits=4,imgcp=img_pc98sbcs,textMapFunc=lambda cc: [0,cc*16],gridMapFunc=lambda cc: [0,cc*16],charCellSizeLF=lambda c,w,h: PC98NotSJISCellSize(c<<8,w,h)))

#-----------------------------------------------------
# PC-98 dbcs sjis
img_pc98dbcs = docImage(16*16,16*16,1)
for hib in range(0x80,0xF0,0x02):
    if hib >= 0xA0 and hib <= 0xDF:
        continue
    #
    imgs = [ None ] * 0x02
    for subrow in range(0,len(imgs)):
        code_base = (hib + subrow) << 8
        img_pc98dbcs.fillrect(0,0,16*16,16*16,0)
        for lob in range(0x40,0x100):
            b1,b2 = DecodeSJIS(hib+subrow,lob)
            if b1 >= 0x20:
                cbmp = PC98FONT.char16x16((b1-0x20)+(b2<<8)) # conversion from unshifted to VRAM means subtracting 0x20
                dx = (lob & 0xF) * 2
                dy = (lob >> 4) * 16
                for y in range(0,16):
                    for x in range(0,2):
                        img_pc98dbcs.rows[dy+y][dx+x] = cbmp[y+(x*16)]
        #
        imgs[subrow] = drawchargrid(imgt8=img_pc98sbcs,tcWidth=8,textMapFunc=lambda cc: [0,cc*16],colDigits=4,imgcp=img_pc98dbcs,charRows=16,charCellWidth=16,charCellHeight=16,code_base=code_base,charCellSizeLF=PC98SJISCellSize)
    #
    code_base = hib << 8
    sc = hex(code_base)[2:]
    while len(sc) < 4:
        sc = '0' + sc
    #
    docWriteBMP("gen-pc98-sjis-"+sc+".bmp",docImageStackCombine(imgs))
    #
    imgs = None

#-----------------------------------------------------
# PC-98 dbcs vidmem
img_pc98dbcs = docImage(16*16,8*16,1)
for hib in range(0x20,0x80,0x04):
    imgs = [ None ] * 0x04
    for subrow in range(0,len(imgs)):
        jisrow = hib + subrow - 0x20
        code_base = (hib + subrow) << 8
        img_pc98dbcs.fillrect(0,0,16*16,8*16,0)
        for jiscol in range(0x01,0x5D):
            cbmp = PC98FONT.char16x16(code_base+jiscol)
            dx = (jiscol & 0xF) * 2
            dy = (jiscol >> 4) * 16
            for y in range(0,16):
                for x in range(0,2):
                    img_pc98dbcs.rows[dy+y][dx+x] = cbmp[y+(x*16)]
        #
        imgs[subrow] = drawchargrid(imgt8=img_pc98sbcs,tcWidth=8,textMapFunc=lambda cc: [0,cc*16],colDigits=4,imgcp=img_pc98dbcs,charRows=8,charCellWidth=16,charCellHeight=16,code_base=code_base,charCellSizeLF=PC98dbcsCellLambda)
    #
    code_base = hib << 8
    sc = hex(code_base)[2:]
    while len(sc) < 4:
        sc = '0' + sc
    #
    docWriteBMP("gen-pc98-tvram-"+sc+".bmp",docImageStackCombine(imgs))
    #
    imgs = None

