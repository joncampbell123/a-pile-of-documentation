#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIPhigh import *

inFile = sys.argv[1]

from apodlib.docHTMLhi import *

class OOXMLReader:
    ok = False
    zipreader = None
    zipmetamap = None
    #
    class relationship:
        Id = None
        Type = None
        Target = None
        def __str__(self):
            r = "[ooxml.relationship"
            if not self.Id == None:
                r += " Id="+str(self.Id)
            if not self.Type == None:
                r += " Type="+str(self.Type)
            if not self.Target == None:
                r += " Target="+str(self.Target)
            r += "]"
            return r
    #
    class zipfilemeta:
        contentType = None
        def __str__(self):
            r = "[zipfilemeta"
            if not self.contentType == None:
                r += " contentType="+str(self.contentType)
            r += "]"
            return r
    #
    def zipmetainit(self,ppath="/"):
        spath = ppath
        if spath == "/":
            spath = ""
        #
        for ent in self.zipreader.opendir(ppath):
            if ent.dtype == 'dir':
                self.zipmetainit(ppath=spath+"/"+ent.dname)
            else:
                fpath = self.zipreader.normalizepath(spath+"/"+ent.dname)
                if not fpath in self.zipmetamap:
                    self.zipmetamap[fpath] = OOXMLReader.zipfilemeta()
    def __init__(self,inFile):
        self.zipmetamap = { }
        self.zipreader = ZIPHighReader(inFile)
        self.zipreader.scan()
        self.zipmetainit()
        self.parsecontenttype()
        rels = self.parserelationshipsfile("/_rels/.rels")
        if rels:
            for rel in rels:
                print(rel)
    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None
    def parserelationshipsfile(self,path):
        rels = [ ]
        #
        if self.zipreader == None:
            return None
        zf = self.zipreader.open(path)
        if zf == None:
            return None
        raw = zf.read()
        xml = HTMLhiReaderState()
        HTMLhiParseAll(raw,xml)
        xroot = xml.getRoot()
        xRels = None
        if xroot:
            for tag in xroot.children:
                if tag.elemType == 'tag':
                    if tag.tag.lower() == 'relationships':
                        xRels = tag
        #
        if xRels:
            for tag in xRels.children:
                if tag.elemType == 'tag':
                    nRel = OOXMLReader.relationship()
                    for attr in tag.attr:
                        if attr.name.lower() == 'id':
                            nRel.Id = attr.value
                        elif attr.name.lower() == 'type':
                            nRel.Type = attr.value
                        elif attr.name.lower() == 'target':
                            nRel.Target = self.zipreader.normalizepath(attr.value)
                    if nRel.Id and nRel.Type and nRel.Target:
                        rels.append(nRel)
        #
        return rels
    def registerZIPContentType(self,path,contenttype,*,policy=None): # WARNING: path is expected to contain normalized path, caller must do it
        if policy == None:
            policy = { }
        if not "replace" in policy:
            policy["replace"] = True
        #
        if not path in self.zipmetamap:
            self.zipmetamap[path] = OOXMLReader.zipfilemeta()
        #
        zmm = self.zipmetamap[path]
        #
        if not policy["replace"] == True and not zmm.contentType == None:
            return
        #
        if contenttype:
            zmm.contentType = contenttype
        else:
            zmm.contentType = None
    def registerZIPContentTypeByExtension(self,ext,contenttype,*,ppath="/"):
        spath = ppath
        if spath == "/":
            spath = ""
        #
        for ent in self.zipreader.opendir(ppath):
            if ent.dtype == 'dir':
                self.registerZIPContentTypeByExtension(ext,contenttype,ppath=spath+"/"+ent.dname)
            else:
                f_ext = None
                chk = ent.dname.lower()
                x = chk.rfind('.')
                if x >= 0:
                    f_ext = chk[x+1:]
                if f_ext == ext:
                    self.registerZIPContentType(self.zipreader.normalizepath(spath+"/"+ent.dname),contenttype,policy={ "replace": False })
    # parse [Content_Types].xml
    def parsecontenttype(self):
        if self.zipreader == None:
            return
        zf = self.zipreader.open("/[Content_Types].xml")
        if zf == None:
            return
        raw = zf.read()
        xml = HTMLhiReaderState()
        HTMLhiParseAll(raw,xml)
        xroot = xml.getRoot()
        xTypes = None
        # look for Types
        if xroot:
            for tag in xroot.children:
                if tag.elemType == 'tag':
                    if tag.tag.lower() == 'types':
                        xTypes = tag
        # found Types, read the Override and Default tags
        if xTypes:
            for tag in xTypes.children:
                if tag.elemType == 'tag':
                    if tag.tag.lower() == 'override':
                        PartName = None
                        ContentType = None
                        for attr in tag.attr:
                            if attr.name.lower() == 'partname':
                                PartName = self.zipreader.normalizepath(attr.value)
                            elif attr.name.lower() == 'contenttype':
                                ContentType = attr.value
                        #
                        if PartName and ContentType:
                            self.registerZIPContentType(PartName,ContentType)
                    #
                    elif tag.tag.lower() == 'default':
                        Extension = None
                        ContentType = None
                        for attr in tag.attr:
                            if attr.name.lower() == 'extension':
                                Extension = attr.value
                            elif attr.name.lower() == 'contenttype':
                                ContentType = attr.value
                        #
                        if Extension and ContentType:
                            self.registerZIPContentTypeByExtension(Extension,ContentType)
                    #
        # done
        del zf
    def dbg_dump_metamap(self):
        print("Debug dump zipmetamap")
        for ent in self.zipmetamap:
            print(str(ent)+": "+str(self.zipmetamap[ent]))
        print("")

zr = OOXMLReader(inFile)
zr.dbg_dump_metamap()
zr.close()

