
import os
import sys
import zlib
import struct

from apodlib.docZIP import *

class ZIPMidReader:
    zipreader = None
    directory = None
    def __init__(self,f):
        self.zipreader = ZIPReader(f)
        self.directory = [ ]
        self.dirbypath = { }
    def scan(self):
        self.directory = [ ]
        self.dirbypath = { }
        self.zipreader.startFromEnd()
        eoc = None
        while True:
            ze = self.zipreader.read()
            if ze == None:
                break
            if isinstance(ze,ZIPEndOfCentralDirectory):
                eoc = ze
        if not eoc:
            return False
        #
        fs = eoc.offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber
        fe = fs + eoc.sizeOfTheCentralDirectory
        self.zipreader.seek(fs)
        while self.zipreader.tell() < fe:
            ze = self.zipreader.read()
            if ze == None:
                break
            if isinstance(ze,ZIPCentralDirectoryFileHeader):
                self.directory.append(ze)
                if ze.filename:
                    self.dirbypath[ze.filename] = ze
        #
        return True
    def readdir(self):
        for ent in self.directory:
            yield ent
    def readpaths(self):
        for name in self.dirbypath:
            yield name
    def lookup(self,name):
        if name in self.dirbypath:
            return self.dirbypath[name]
        return None
    def open(self,f):
        if isinstance(f,bytes):
            x = self.lookup(f)
            if x == None:
                return None
            return self.zipreader.open(x)
        #
        return self.zipreader.open(f)
    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None

