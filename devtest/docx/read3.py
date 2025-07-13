#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

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

inFile = sys.argv[1]

zr = ZIPMidReader(inFile)
zr.scan()
#
print("**DIR**")
for ent in zr.readdir():
    print(ent)
#
print("**PATHS**")
for name in zr.readpaths():
    print(name)
#
print("**LOOKUPS**")
for name in zr.readpaths():
    print(name)
    lu = zr.lookup(name)
    print(lu)
#
print("**OPEN-BY-NAME**")
for name in zr.readpaths():
    print("* OPEN "+str(name))
    lu = zr.lookup(name)
    print("* LOOKUP "+str(lu))
    f = zr.open(name)
    if f:
        b = f.read()
        print(b)
        del f
    else:
        print("!! FAILED TO OPEN !!")
#
print("**OPEN-BY-OBJ**")
for name in zr.readpaths():
    print("* OPEN "+str(name))
    lu = zr.lookup(name)
    print("* LOOKUP "+str(lu))
    f = zr.open(lu)
    if f:
        b = f.read()
        print(b)
        del f
    else:
        print("!! FAILED TO OPEN !!")
#
zr.close()

