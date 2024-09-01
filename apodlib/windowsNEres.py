
import struct

class WindowsNEResourceReader:
    rawbin = None
    rscAlignShift = None
    resByType = None
    class resType:
        res = None
    class resEntry:
        rnOffset = None
        rnLength = None
        rnFlags = None
        rnId = None
        data = None
        # ignore rnHandle and rnUsage
    #
    def parse(self,raw):
        # MS-DOS exe header or bust
        if not raw[0:2] == b"MZ":
            raise Exception("Not an EXE")
        # offset at 0x3C, points to NE header
        winofs = struct.unpack("<L",raw[0x3C:0x40])[0]
        if winofs < 0x40 or winofs >= len(raw):
            raise Exception("No Windows header")
        # "NE" at offset
        if not raw[winofs:winofs+2] == b"NE":
            raise Exception("Not an NE header")
        # we only care about resources.
        resofs = struct.unpack("<H",raw[winofs+0x24:winofs+0x26])[0] + winofs
        # resource header
        self.rscAlignShift = struct.unpack("<H",raw[resofs+0x00:resofs+0x02])[0]
        rdo = resofs+0x02
        self.resByType = { }
        while True:
            rtTypeId,rtResourceCount = struct.unpack("<HH",raw[rdo:rdo+4])
            if rtTypeId == 0:
                break
            rdo += 4+4 # skip rtReserved
            #
            if (rtTypeId & 0x8000):
                resKey = rtTypeId & 0x7FFF
            else:
                nameo = rtTypeId + resofs
                namel = raw[nameo] # length of name
                resKey = raw[nameo+1:nameo+1+namel]
            #
            rtent = self.resType()
            rtent.res = { }
            #
            for i in range(0,rtResourceCount):
                ent = self.resEntry()
                ent.rnOffset,ent.rnLength,ent.rnFlags,ent.rnId = struct.unpack("<HHHH",raw[rdo:rdo+8])
                ent.rnOffset = ent.rnOffset << self.rscAlignShift
                ent.rnLength = ent.rnLength << self.rscAlignShift # Microsoft's NE documentation is a liar, the length is in AlignShift units, not bytes
                ent.data = raw[ent.rnOffset:ent.rnOffset+ent.rnLength]
                rdo += 8 + 4 # ignore rnHandle,rnUsage
                #
                if (ent.rnId & 0x8000):
                    ent.rnId = ent.rnId & 0x7FFF
                else:
                    nameo = ent.rnId + resofs
                    namel = raw[nameo] # length of name
                    ent.rnId = raw[nameo+1:nameo+1+namel]
                #
                if ent.rnId in rtent.res:
                    raise Exception("Resource ID already exists")
                rtent.res[ent.rnId] = ent
            #
            if resKey in self.resByType:
                raise Exception("Resource type already exists")
            self.resByType[resKey] = rtent
        #
    def getResource(self,resTypeID,resID):
        if not self.resByType == None:
            if resTypeID in self.resByType:
                rtent = self.resByType[resTypeID].res
                if resID in rtent:
                    return rtent[resID]
        #
        return None
    def listResourceTypes(self):
        if self.resByType == None:
            return [ ]
        return self.resByType.keys()
    def listResources(self,typeId):
        if self.resByType == None:
            return [ ]
        if not typeId in self.resByType:
            return [ ]
        return self.resByType[typeId].res.keys()
    def __init__(self,*,path=None):
        if not path == None:
            f = open(path,mode="rb")
            self.rawbin = f.read()
            f.close()
        else:
            raise Exception("Nothing provided to parse")
        #
        self.parse(self.rawbin)


