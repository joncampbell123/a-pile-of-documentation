#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

inFile = sys.argv[1]

# number of this disk             2 bytes
# number of the disk with the
# start of the central directory  2 bytes
# total number of entries in
# the central dir on this disk    2 bytes
# total number of entries in
# the central dir                 2 bytes
# size of the central directory   4 bytes
# offset of start of central
# directory with respect to
# the starting disk number        4 bytes
# zipfile comment length          2 bytes
#                                =18 bytes
#
# zipfile comment (variable size)

class ZIPEndOfCentralDirectory:
    signature = 0x06054b50
    numberOfThisDisk = None
    numberOfTheDiskWithTheStartOfTheCentralDirectory = None
    totalNumberOfEntriesInTheCentralDirOnThisDisk = None
    totalNumberOfEntriesInTheCentralDir = None
    sizeOfTheCentralDirectory = None
    offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber = None
    zipfileCommentLength = None
    zipfileComment = None
    #
    dataOffset = None
    #
    def __init__(self,f):
        if f:
            [
                self.numberOfThisDisk,
                self.numberOfTheDiskWithTheStartOfTheCentralDirectory,
                self.totalNumberOfEntriesInTheCentralDirOnThisDisk,
                self.totalNumberOfEntriesInTheCentralDir,
                self.sizeOfTheCentralDirectory,
                self.offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber,
                self.zipfileCommentLength
            ] = struct.unpack("<HHHHLLH",f.read(18))
            if not self.zipfileCommentLength == None and self.zipfileCommentLength > 0:
                self.zipfileComment = f.read(self.zipfileCommentLength)
            #
            self.dataOffset = f.tell()
    def __str__(self):
        r = "[ZIPEndOfCentralDirectory"
        if not self.sizeOfTheCentralDirectory == None:
            r += " cdsize="+str(self.sizeOfTheCentralDirectory)
        if not self.offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber == None:
            r += " cdofs="+str(self.offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber)
        if not self.zipfileComment == None:
            r += " comment="+str(self.zipfileComment)
        if not self.dataOffset == None:
            r += " dataoffset="+str(self.dataOffset)
        r += "]"
        return r

# version made by                 2 bytes
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
# file comment length             2 bytes
# disk number start               2 bytes
# internal file attributes        2 bytes
# external file attributes        4 bytes
# relative offset of local header 4 bytes
#                                 =42 bytes
#
# filename (variable size)
# extra field (variable size)
# file comment (variable size)

class ZIPCentralDirectoryFileHeader:
    signature = 0x02014b50
    versionMadeBy = None
    versionNeededToExtract = None
    generalPurposeBitFlag = None
    compressionMethod = None
    lastModFileTime = None
    lastModFileDate = None
    crc32 = None
    compressedSize = None
    uncompressedSize = None
    filenameLength = None
    extraFieldLength = None
    fileCommentLength = None
    diskNumberStart = None
    internalFileAttributes = None
    externalFileAttributes = None
    relativeOffsetOfLocalHeader = None
    filename = None
    extraField = None
    fileComment = None
    #
    dataOffset = None
    #
    def __init__(self,f):
        if f:
            [
                self.versionMadeBy,
                self.versionNeededToExtract,
                self.generalPurposeBitFlag,
                self.compressionMethod,
                self.lastModFileTime,
                self.lastModFileDate,
                self.crc32,
                self.compressedSize,
                self.uncompressedSize,
                self.filenameLength,
                self.extraFieldLength,
                self.fileCommentLength,
                self.diskNumberStart,
                self.internalFileAttributes,
                self.externalFileAttributes,
                self.relativeOffsetOfLocalHeader
            ] = struct.unpack("<HHHHHHLLLHHHHHLL",f.read(42))
            if not self.filenameLength == None and self.filenameLength > 0:
                self.filename = f.read(self.filenameLength)
            if not self.extraFieldLength == None and self.extraFieldLength > 0:
                self.extraField = f.read(self.extraFieldLength)
            if not self.fileCommentLength == None and self.fileCommentLength > 0:
                self.fileComment = f.read(self.fileCommentLength)
            #
            self.dataOffset = f.tell()
    def __str__(self):
        r = "[ZIPCentralDirectoryFileHeader"
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
        if not self.relativeOffsetOfLocalHeader == None:
            r += " lhoffset="+str(self.relativeOffsetOfLocalHeader)
        if not self.extraField == None:
            r += " extra="+str(self.extraField)
        if not self.fileComment == None:
            r += " comment="+str(self.fileComment)
        if not self.dataOffset == None:
            r += " dataoffset="+str(self.dataOffset)
        r += "]"
        return r

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
#
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
            [
                self.versionNeededToExtract,
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

class ZIPReaderFile:
    zipreader = None # ZIPReader
    filePos = None
    readPos = None
    fileSize = None
    seekable = False
    zlibdec = None
    zlibmore = None
    dataOffset = None
    compressedSize = None
    compressionMethod = None
    def __init__(self,zr,fh):
        self.zipreader = zr
        #
        if isinstance(fh,ZIPLocalFileHeader):
            self.compressionMethod = fh.compressionMethod
            self.compressedSize = fh.compressedSize
            self.fileSize = fh.uncompressedSize
            self.dataOffset = fh.dataOffset
        elif isinstance(fh,ZIPCentralDirectoryFileHeader):
            self.compressionMethod = fh.compressionMethod
            self.compressedSize = fh.compressedSize
            self.fileSize = fh.uncompressedSize
            self.dataOffset = None
            # then look up local file header
            oldPos = self.zipreader.scanPos
            self.zipreader.scanPos = fh.relativeOffsetOfLocalHeader
            lh = self.zipreader.read()
            if lh == None or not isinstance(lh,ZIPLocalFileHeader):
                raise Exception("Unable to look up local file header")
            self.zipreader.scanPos = oldPos
            self.dataOffset = lh.dataOffset
        else:
            raise Exception("Unexpected object")
        #
        self.filePos = 0
        self.readPos = 0
        if self.compressionMethod == 0: # store
            self.seekable = True
        elif self.compressionMethod == 8: # deflate
            self.zlibdec = zlib.decompressobj(-15)
            self.zlibmore = bytes()
    def seek(self,pos):
        if self.seekable:
            if pos < 0:
                pos = 0
            if pos > self.fileSize:
                pos = self.fileSize
            self.filePos = self.readPos = pos
    def rewind(self):
        self.filePos = 0
        self.readPos = 0
        if self.zlibdec:
            del self.zlibdec
        if self.compressionMethod == 8: # deflate
            self.zlibdec = zlib.decompressobj(-15)
            self.zlibmore = bytes()
    def __del__(self):
        if self.zlibdec:
            del self.zlibdec
    def size(self):
        return self.fileSize
    def read(self,n=None):
        if self.compressionMethod == 0: # store
            return self.readStore(n)
        elif self.compressionMethod == 8: # deflate
            return self.readDeflate(n)
        return None
    def readStore(self,n=None):
        rem = self.fileSize - self.filePos
        if not n == None and rem > n:
            rem = n
        if rem > 0:
            self.zipreader.fileObject.seek(self.dataOffset+self.filePos)
            b = self.zipreader.fileObject.read(rem)
            if not b == None:
                self.filePos += len(b)
                return b
        #
        return None
    def readDeflate(self,n=None):
        crem = self.compressedSize - self.readPos
        rem = self.fileSize - self.filePos
        if not n == None and rem > n:
            rem = n
        #
        if self.zlibdec.eof:
            return None
        #
        rb = bytes()
        while rem > 0:
            self.zipreader.fileObject.seek(self.dataOffset+self.readPos)
            #
            if crem > 0:
                zb = self.zipreader.fileObject.read(crem)
                if not zb == None:
                    self.readPos += len(zb)
                    self.zlibmore += zb
                    crem -= len(zb)
            #
            if len(self.zlibmore) == 0:
                break
            #
            ub = self.zlibdec.decompress(self.zlibmore,rem)
            if self.zlibdec.unconsumed_tail:
                self.zlibmore = self.zlibdec.unconsumed_tail
            else:
                self.zlibmore = bytes()
            #
            self.filePos += len(ub)
            rem -= len(ub)
            rb += ub
            #
            if self.zlibdec.eof:
                break
        #
        if len(rb) > 0:
            return rb
        #
        return None

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
        b = self.fileObject.read(4)
        if len(b) < 4:
            return None
        sig = struct.unpack("<L",b)[0]
        #print(str(sig)+" "+str(self.fileObject.tell()))
        if sig == ZIPLocalFileHeader.signature:
            zh = ZIPLocalFileHeader(self.fileObject)
            if zh.generalPurposeBitFlag & 8: # stream compression, and the crc32/compressed/uncompressed are appended to the end
                self.scanPos = self.fileObject.seek(0,2) # we do not support this!
                return None
            self.scanPos = self.fileObject.tell() + zh.compressedSize
            return zh
        if sig == ZIPCentralDirectoryFileHeader.signature:
            zh = ZIPCentralDirectoryFileHeader(self.fileObject)
            self.scanPos = self.fileObject.tell()
            return zh
        if sig == ZIPEndOfCentralDirectory.signature:
            zh = ZIPEndOfCentralDirectory(self.fileObject)
            self.scanPos = self.fileObject.tell()
            return zh
        return None
    def readall(self):
        while True:
            ent = self.read()
            if ent == None:
                break
            yield ent
    def open(self,what):
        if isinstance(what,ZIPLocalFileHeader) or isinstance(what,ZIPCentralDirectoryFileHeader):
            return ZIPReaderFile(self,what)
        return None

zr = ZIPReader(inFile)
#
for ze in zr.readall():
    print(ze)
    zf = zr.open(ze)
    if not zf == None:
        b = zf.read()
        print("Length "+str(zf.size())+"/"+str(len(b)))
        print("Data: "+str(b))
        if not zf.size() == len(b):
            print("WARNING: Size mismatch")
#
zr.close()

