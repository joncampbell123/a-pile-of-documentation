
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

