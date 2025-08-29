
import os
import sys
import zlib
import struct

from apodlib.docZIPhigh import *
from apodlib.docHTMLhi import *

class OpenDocumentReader:
    ok = False
    zipreader = None
    #
    def __init__(self,inFile):
        self.zipreader = ZIPHighReader(inFile)
        self.zipreader.scan()
        self.ok = True
    #
    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None
    #
    def opendata(self,path):
        if self.zipreader == None:
            return None
        zf = self.zipreader.open(path)
        if zf == None:
            return None
        #
        return zf
    #
    def closedata(self,zf):
        del zf
    #
    def readdata(self,path):
        if self.zipreader == None:
            return None
        zf = self.zipreader.open(path)
        if zf == None:
            return None
        raw = zf.read()
        del zf
        #
        return raw
    #
    def readxml(self,path):
        if self.zipreader == None:
            return None
        zf = self.zipreader.open(path)
        if zf == None:
            return None
        raw = zf.read()
        xml = HTMLhiReaderState()
        HTMLhiParseAll(raw,xml)
        del zf
        #
        return xml.getRoot()
    #
    def dbg_dump(self):
        print("Debug dump")
        print("  ok="+str(self.ok))
        #
        print("Debug dump files")
        self.dbg_dump_files()
    #
    def dbg_dump_files(self,ppath="/"):
        spath = ppath
        if spath == "/":
            spath = ""
        #
        for ent in self.zipreader.opendir(ppath):
            if ent.dtype == 'dir':
                self.dbg_dump_files(ppath=spath+"/"+ent.dname)
            else:
                fpath = self.zipreader.normalizepath(spath+"/"+ent.dname)
                print("  "+fpath)

