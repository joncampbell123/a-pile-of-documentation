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

    def opendir(self,path=None):
        class direntstruct:
            dtype = None
            dname = None
            zippath = None
            def __str__(self):
                r = "[direntstruct"
                if not self.dtype == None:
                    r += " dtype="+str(self.dtype)
                if not self.dname == None:
                    r += " dname="+str(self.dname)
                if not self.zippath == None:
                    r += " zippath="+str(self.zippath)
                if not self.fpath == None:
                    r += " fpath="+str(self.fpath)
                r += "]"
                return r
        class dirent:
            fpath = None
            cdir = None
            cit = None
            def __init__(self,cdir):
                self.cdir = cdir
                self.cit = iter(cdir.contents.keys())
            def rewind(self):
                self.cit = iter(cdir.contents.keys())
            def readdir(self):
                try:
                    nxt = next(self.cit)
                    nv = self.cdir.contents[nxt]
                    rsp = direntstruct()
                    rsp.fpath = self.fpath + "/" + nxt
                    rsp.cdir = self.cdir
                    rsp.dname = nxt
                    if isinstance(nv,ZIPHighReader.Directory):
                        rsp.dtype = "dir"
                    else:
                        rsp.dtype = "file"
                        rsp.zippath = nv
                    return rsp
                except StopIteration:
                    return None
            def __iter__(self):
                return self
            def __next__(self):
                x = self.readdir()
                if x == None:
                    raise StopIteration
                return x
        #
        if path == None:
            path = ""
        #
        resp = self.pathtoelems(path+"/")
        if resp == None:
            return
        pathelems = resp.pathelems
        if pathelems == None:
            return
        fname = resp.fname
        if not fname == None: # we did a directory (trailing slash) lookup
            return
        fpath = ""
        cdir = self.rootdir
        for ent in pathelems:
            if isinstance(cdir.contents[ent],ZIPHighReader.Directory):
                fpath = fpath + "/" + ent
                cdir = cdir.contents[ent]
            else:
                return
        #
        dr = dirent(cdir)
        dr.fpath = fpath
        return dr

    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None

def opendirenum(zr,path=None):
    if path == None:
        path = ""
    #
    for x in zr.opendir(path):
        print(x)
        if x.dtype == 'dir':
            opendirenum(zr,path+"/"+x.dname)

zr = ZIPHighReader(inFile)
zr.scan()
zr.dbg_dump_dirs()
opendirenum(zr)
zr.close()

