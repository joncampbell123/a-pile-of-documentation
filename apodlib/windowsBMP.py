
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

