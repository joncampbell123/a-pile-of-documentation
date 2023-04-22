
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

