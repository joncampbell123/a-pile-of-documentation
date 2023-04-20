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
    palette = None # array of docRGBA
    bits_per_pixel = None
    bytes_per_pixel = None
    readpixelp = None
    writepixelp = None
    def __init__(self,w,h,bpp):
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
        self.rows = [ 0 ] * self.height
        for i in range(0,self.height):
            self.rows[i] = bytearray(self.stride)
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
    def readpixel(self,x,y):
        if y >= 0 and y < len(self.rows):
            rp = self.rows[y]
            if not rp == None:
                return self.readpixelp(rp,x)
        return None
    def writepixel(self,x,y,c):
        if y >= 0 and y < len(self.rows):
            rp = self.rows[y]
            if not rp == None and x >= 0:
                self.writepixelp(rp,x,c)
    def readpixel_1(self,rp,x):
        byo = x >> 3
        bio = x & 7
        if byo < len(rp):
            return (rp[byo] >> (7-bio)) & 0x1
        return None
    def readpixel_4(self,rp,x):
        return None
    def readpixel_8(self,rp,x):
        if x < len(rp):
            return rp[x]
        return None
    def readpixel_15(self,rp,x):
        return None
    def readpixel_16(self,rp,x):
        return None
    def readpixel_24(self,rp,x):
        return None
    def readpixel_32(self,rp,x):
        return None
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

def imgmonocopy(dimg,dx,dy,w,h,simg,sx,sy,lf):
    for y in range(0,h):
        for x in range(0,w):
            dimg.writepixel(dx+x,dy+y,lf(simg.readpixel(sx+x,sy+y)))

def drawsbcsgrid(imgcp,charCellWidth,charCellHeight):
    charGridX = 1+(charCellWidth*2)
    charGridY = 1+charCellHeight
    img = docImage(((charCellWidth+1)*16)+charGridX,((charCellHeight+1)*16)+charGridY,8)
    #
    img.palette_used = 3
    img.palette[0] = docRGBA(0,0,0,0)
    img.palette[1] = docRGBA(255,255,255,255)
    img.palette[2] = docRGBA(63,63,192)
    #
    img.fillrect(0,0,img.width,img.height,1)
    img.fillrect(charGridX-1,charGridY-1,img.width,charGridY,2)
    img.fillrect(charGridX-1,charGridY-1,charGridX,img.height,2)
    for r in range(0,17):
        img.fillrect(charGridX,(r*17)+charGridY-1,img.width,(r*17)+charGridY,2)
    for c in range(0,17):
        img.fillrect((c*9)+charGridX-1,charGridY,(c*9)+charGridX,img.height,2)
    #
    for r in range(0,16):
        s = hex(r)[2:].upper()
        sx = int(ord(s[0]) % 16) * 8
        sy = int(ord(s[0]) / 16) * 16
        dx = charGridX + (r * 9)
        dy = 0
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        #
        dx = 0
        dy = charGridY + (r * 17)
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        sx = int(ord('0') % 16) * 8
        sy = int(ord('0') / 16) * 16
        dx = 8
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
    #
    for r in range(0,16):
        for c in range(0,16):
            sx = c * 8
            sy = r * 16
            dx = charGridX + (c * 9)
            dy = charGridY + (r * 17)
            imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: _x)
    #
    return img

#-----------------------------------------------------
docWriteBMP("gen-cp437.bmp",drawsbcsgrid(docLoadBMP("ref/cp437vga8x16.bmp"),8,16))

#-----------------------------------------------------
docWriteBMP("gen-cp850.bmp",drawsbcsgrid(docLoadBMP("ref/cp850vga8x16.bmp"),8,16))

#-----------------------------------------------------
docWriteBMP("gen-cp851.bmp",drawsbcsgrid(docLoadBMP("ref/cp851vga8x16.bmp"),8,16))

#-----------------------------------------------------
docWriteBMP("gen-cp852.bmp",drawsbcsgrid(docLoadBMP("ref/cp852vga8x16.bmp"),8,16))

#-----------------------------------------------------
docWriteBMP("gen-cp853.bmp",drawsbcsgrid(docLoadBMP("ref/cp853vga8x16.bmp"),8,16))

#-----------------------------------------------------
docWriteBMP("gen-cp866.bmp",drawsbcsgrid(docLoadBMP("ref/cp866vga8x16.bmp"),8,16))

#-----------------------------------------------------
# PC-98 FONT ROM, video memory text codes

def drawsbcsgrid_pc98(imgcp,charCellWidth,charCellHeight):
    charGridX = 1+(charCellWidth*4)
    charGridY = 1+charCellHeight
    img = docImage(((charCellWidth+1)*16)+charGridX,((charCellHeight+1)*16)+charGridY,8)
    #
    img.palette_used = 3
    img.palette[0] = docRGBA(0,0,0,0)
    img.palette[1] = docRGBA(255,255,255,255)
    img.palette[2] = docRGBA(63,63,192)
    #
    img.fillrect(0,0,img.width,img.height,1)
    img.fillrect(charGridX-1,charGridY-1,img.width,charGridY,2)
    img.fillrect(charGridX-1,charGridY-1,charGridX,img.height,2)
    for r in range(0,17):
        img.fillrect(charGridX,(r*17)+charGridY-1,img.width,(r*17)+charGridY,2)
    for c in range(0,17):
        img.fillrect((c*9)+charGridX-1,charGridY,(c*9)+charGridX,img.height,2)
    #
    for r in range(0,16):
        s = hex(r)[2:].upper()
        sx = int(ord(s[0]) % 16) * 8
        sy = int(ord(s[0]) / 16) * 16
        dx = charGridX + (r * 9)
        dy = 0
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        #
        dx = 16
        dy = charGridY + (r * 17)
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        sx = int(ord('0') % 16) * 8
        sy = int(ord('0') / 16) * 16
        dx = 0
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        dx = 8
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
        dx = 24
        imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: (_x ^ 1))
    #
    for r in range(0,16):
        for c in range(0,16):
            sx = c * 8
            sy = r * 16
            dx = charGridX + (c * 9)
            dy = charGridY + (r * 17)
            imgmonocopy(img,dx,dy,8,16,imgcp,sx,sy,lambda _x: _x)
    #
    return img



f = open("ref/pc98font.rom",mode="rb")
pc98rom = f.read()
f.close()
# at 0x00000 = 8x8 single wide 8-bit character cells (not used here)
# at 0x00800 = 8x16 single wide 8-bit character cells
# at 0x01800 = 96x92 double wide character cells
# render the sbcs
img_pc98sbcs = docImage(8*16,16*16,1)
img_pc98sbcs.palette_used = 2
img_pc98sbcs.palette[0] = docRGBA(0,0,0,0)
img_pc98sbcs.palette[1] = docRGBA(255,255,255,255)
for c in range(0,256):
    ofs = 0x800+(c*16)
    cb = c&0xF
    rb = (c>>4)*16
    for r in range(0,16):
        img_pc98sbcs.rows[r+rb][cb] = pc98rom[ofs+r]
#
docWriteBMP("gen-pc98-tvram-0-sbcs.bmp",drawsbcsgrid_pc98(img_pc98sbcs,8,16))
#
pc98rom = None
img_pc98sbcs = None

