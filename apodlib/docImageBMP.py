
from apodlib.docImage import *
from apodlib.windowsBMP import *

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

