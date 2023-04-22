#!/usr/bin/python3

import os
import re
import sys
import csv
import math
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.ShiftJIS import *
from apodlib.docImage import *
from apodlib.windowsBMP import *
from apodlib.windowsFNT import *
from apodlib.docImageBMP import *
from apodlib.NECPC98FONTROM import *

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

def loadAndRenderWindowsFNT(path):
    # Windows code page 1252, System font extracted from Windows 3.1
    win31sysfnt = MSWINFNT(path)
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
    return drawchargrid(tcWidth=textw,textMapFunc=lambda cc: [(cc&0xF)*wgridw,(cc>>4)*wgridh],imgcp=wgrid,charCellWidth=wgridw,charCellHeight=wgridh)

#-----------------------------------------------------
# Windows FNT font files
docWriteBMP("gen-windows31-cp1252-system.bmp",loadAndRenderWindowsFNT("ref/window31_system_font_cp1252.fnt"))
docWriteBMP("gen-windows31-cp1252-fixedsys.bmp",loadAndRenderWindowsFNT("ref/window31_fixedsys_font_cp1252.fnt"))
docWriteBMP("gen-windows31-cp1252-sans-serif-8pt.bmp",loadAndRenderWindowsFNT("ref/window31_sans_serif_8pt_font_cp1252.fnt"))

#-----------------------------------------------------
PC98FONT = PC98FONTROM(path="ref/pc98font.rom")

def PC98IsSJIS(cc):
    return IsWordSJIS(cc)

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

