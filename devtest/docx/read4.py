#!/usr/bin/python3

import os
import re
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIPmid import *

inFile = sys.argv[1]

class ZIPHighReader:
    class Directory:
        contents = None
        def __init__(self):
            self.contents = { }
    #
    encoding = 'UTF-8'
    zipreader = None
    rootdir = None
    def __init__(self,f):
        self.zipreader = ZIPMidReader(f)
    def scan(self):
        self.zipreader.scan()
        self.rootdir = ZIPHighReader.Directory()
        #
        for path in self.zipreader.readpaths():
            origpath = path
            path = path.decode(self.encoding)
            origpathstr = path
            path = re.sub(r'/+',r'/',path)
            if len(path) > 0 and path[0] == '/': # remove leading /
                path = path[1:]
            if len(path) > 0 and path[-1] == '/': # if a trailing /, it's a directory
                continue
            if len(path) == 0: # null name? forget it
                continue
            pathelems = path.split('/')
            if len(pathelems) == 0:
                continue
            fname = pathelems.pop()
            if fname == "." or fname == "..":
                return
            #
            cdir = self.rootdir
            for ent in pathelems:
                if ent == "." or ent == "..":
                    break
                if ent in cdir.contents:
                    ce = cdir.contents[ent]
                    if not isinstance(ce,ZIPHighReader.Directory):
                        raise Exception("ZIPHigh directory re-defined as file: "+origpathstr)
                else:
                    cdir.contents[ent] = ZIPHighReader.Directory()
                    ce = cdir.contents[ent]
                cdir = ce
            #
            if fname in cdir.contents:
                raise Exception("ZIPHigh redefined file: "+origpathstr)
            cdir.contents[fname] = origpath
    def dbg_dump_dirs(self,cdir=None,cpath=""):
        if cdir == None:
            cdir = self.rootdir
        #
        print("ZIPHIGH debug dump of "+cpath)
        for ent in cdir.contents:
            if isinstance(cdir.contents[ent],ZIPHighReader.Directory):
                self.dbg_dump_dirs(cdir.contents[ent],cpath+"/"+ent)
                print("ZIPHIGH debug dump of "+cpath)
            else:
                print("  "+ent+" -> "+cdir.contents[ent].decode(self.encoding))
    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None

zr = ZIPHighReader(inFile)
zr.scan()
zr.dbg_dump_dirs()
zr.close()

