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

    def pathtoelems(self,path):
        fname = None
        path = re.sub(r'/+',r'/',path)
        pathelems = path.split('/')
        if len(pathelems) > 0 and pathelems[0] == "":
            pathelems = pathelems[1:]
        if len(pathelems) > 0:
            fname = pathelems.pop()
            if fname == "":
                fname = None
        #
        class PTEResponse:
            fname = None
            pathelems = None
        #
        resp = PTEResponse()
        resp.fname = fname
        resp.pathelems = pathelems
        #
        return resp

    def scan(self):
        self.zipreader.scan()
        self.rootdir = ZIPHighReader.Directory()
        #
        for path in self.zipreader.readpaths():
            origpath = path
            path = path.decode(self.encoding)
            origpathstr = path
            resp = self.pathtoelems(path)
            if resp == None:
                continue
            pathelems = resp.pathelems
            if pathelems == None:
                continue
            fname = resp.fname
            if fname == None:
                continue # can happen for /directory/ entries that end in a slash, which we want to skip
            #
            cdir = self.rootdir
            for ent in pathelems:
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

