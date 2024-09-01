
from apodlib.docImage import *

import zlib
import struct

def docWritePNGChunk(f,chunkID,chunkData=b""):
    # <LENGTH> <CHUNK TYPE> <DATA> <CRC>
    f.write(struct.pack(">L",len(chunkData)))
    if not len(chunkID) == 4:
        raise Exception("PNG chunkID not 4 chars")
    #
    f.write(chunkID)
    #
    if len(chunkData) > 0:
        f.write(chunkData)
    #
    f.write(struct.pack(">L",zlib.crc32(chunkID + chunkData)))

def docWritePNG(path,image):
    f = open(path,"wb")
    # PNG signature
    f.write(bytes([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A]))
    # IHDR
    #  L  WIDTH
    #  L  HEIGHT
    #  B  BIT DEPTH
    #  B  COLOR TYPE
    #  B  COMPRESSION METHOD
    #  B  FILTER METHOD
    #  B  INTERLACE METHOD
    iWidth = image.width
    iHeight = image.height
    iBitDepth = image.bits_per_pixel
    if image.bits_per_pixel == 1 or image.bits_per_pixel == 4 or image.bits_per_pixel == 8:
        iColorType = 3 # indexed color
    elif image.bits_per_pixel == 24:
        iColorType = 2 # truecolor
    elif image.bits_per_pixel == 32:
        iColorType = 6 # truecolor with alpha
    else:
        raise Exception("Unknown image format")
    iCompressMethod = 0 # zlib
    iFilterMethod = 0 # none/adaptive
    iInterlace = 0 # no interlacing
    docWritePNGChunk(f,b"IHDR",struct.pack(">LLBBBBB",iWidth,iHeight,iBitDepth,iColorType,iCompressMethod,iFilterMethod,iInterlace));
    # PLTE
    if not image.palette == None:
        palsz = len(image.palette)
        if palsz > image.palette_used:
            palsz = image.palette_used
        if palsz > 0:
            pal = bytearray(palsz*3)
            for pi in range(0,palsz):
                pal[(pi*3)+0] = image.palette[pi].R
                pal[(pi*3)+1] = image.palette[pi].G
                pal[(pi*3)+2] = image.palette[pi].B
            docWritePNGChunk(f,b"PLTE",pal)
    # IDAT
    zz = zlib.compressobj(level=9,wbits=15)
    bypp = ((image.width*image.bits_per_pixel) + 7) >> 3
    idat = b""
    for y in range(0,image.height):
        row = bytes([0]) + image.rows[y][0:bypp] # filter byte + image data
        idat += zz.compress(row)
    idat += zz.flush()
    docWritePNGChunk(f,b"IDAT",idat)
    # IEND
    docWritePNGChunk(f,b"IEND")
    # done
    f.close()

