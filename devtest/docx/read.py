#!/usr/bin/python3

import os
import sys
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

inFile = sys.argv[1]

# local file header signature     4 bytes  (0x04034b50)
# version needed to extract       2 bytes
# general purpose bit flag        2 bytes
# compression method              2 bytes
# last mod file time              2 bytes
# last mod file date              2 bytes
# crc-32                          4 bytes
# compressed size                 4 bytes
# uncompressed size               4 bytes
# filename length                 2 bytes
# extra field length              2 bytes
#                                =26 bytes

# filename (variable size)
# extra field (variable size)

class ZIPLocalFileHeader:
    signature = 0x04034b50 # PK\x03\0x4
    versionNeededToExtract = None # version needed to extract
    generalPurposeBitFlag = None # general purpose bit flag
    compressionMethod = None # compression method
    lastModFileTime = None # last mod file time
    lastModFileDate = None # last mod file date
    crc32 = None # crc-32
    compressedSize = None # compressed size
    uncompressedSize = None # uncompressed size
    filenameLength = None # filename length
    extraFieldLength = None # extra field length
    filename = None # filename
    extraField = None # extraField
    #
    dataOffset = None
    #
    def __init__(self,f):
        if f:
            [   self.versionNeededToExtract,
                self.generalPurposeBitFlag,
                self.compressionMethod,
                self.lastModFileTime,
                self.lastModFileDate,
                self.crc32,
                self.compressedSize,
                self.uncompressedSize,
                self.filenameLength,
                self.extraFieldLength
            ] = struct.unpack("<HHHHHLLLHH",f.read(26))
            if not self.filenameLength == None and self.filenameLength > 0:
                self.filename = f.read(self.filenameLength)
            if not self.extraFieldLength == None and self.extraFieldLength > 0:
                self.extraField = f.read(self.extraFieldLength)
            #
            self.dataOffset = f.tell()
    def __str__(self):
        r = "[ZIPLocalFileHeader"
        if not self.versionNeededToExtract == None:
            r += " versionNeed="+str(self.versionNeededToExtract)
        if not self.generalPurposeBitFlag == None:
            r += " genBitFlag="+hex(self.generalPurposeBitFlag)
        if not self.compressionMethod == None:
            r += " compression="+str(self.compressionMethod)
        if not self.filename == None:
            r += " filename="+str(self.filename)
        if not self.compressedSize == None:
            r += " csize="+str(self.compressedSize)
        if not self.uncompressedSize == None:
            r += " usize="+str(self.uncompressedSize)
        if not self.dataOffset == None:
            r += " dataoffset="+str(self.dataOffset)
        if not self.extraField == None:
            r += " extra="+str(self.extraField)
        r += "]"
        return r

class ZIPReader:
    fileObject = None
    scanPos = None
    def __init__(self,f):
        if isinstance(f,str):
            self.fileObject = open(f,"rb")
        else:
            self.fileObject = f
        #
        self.scanPos = 0
    def close(self):
        if self.fileObject:
            self.fileObject.close()
        self.fileObject = None
    def seek(self,pos):
        if self.fileObject:
            self.scanPos = pos
            return self.fileObject.seek(pos)
        return None
    def read(self):
        if not self.fileObject:
            return None
        #
        if not self.fileObject.tell() == self.scanPos:
            self.fileObject.seek(self.scanPos)
        #
        sig = struct.unpack("<L",self.fileObject.read(4))[0]
        #print(str(sig)+" "+str(self.fileObject.tell()))
        if sig == ZIPLocalFileHeader.signature:
            zh = ZIPLocalFileHeader(self.fileObject)
            if zh.generalPurposeBitFlag & 8: # stream compression, and the crc32/compressed/uncompressed are appended to the end
                self.scanPos = self.fileObject.seek(0,2) # we do not support this!
                return None
            self.scanPos = self.fileObject.tell() + zh.compressedSize
            return zh
        return None
    def readall(self):
        while True:
            ent = self.read()
            if ent == None:
                break
            yield ent

zr = ZIPReader(inFile)
for ze in zr.readall():
    print(ze)
zr.close()

