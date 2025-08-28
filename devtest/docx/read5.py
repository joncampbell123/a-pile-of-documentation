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
    documentPath = None
    corePropertiesPath = None
    extendedPropertiesPath = None
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
    #
    def __init__(self,inFile):
        self.zipmetamap = { }
        self.zipreader = ZIPHighReader(inFile)
        self.zipreader.scan()
        self.zipmetainit()
        self.parsecontenttype()
        #
        rels = self.parserelationshipsfile("/_rels/.rels")
        if rels:
            for relname in rels:
                rel = rels[relname]
                if rel.Target and rel.Type and rel.Id == relname:
                    if re.search(r'\/officeDocument$',rel.Type,flags=re.IGNORECASE):
                        self.documentPath = self.zipreader.normalizepath(rel.Target)
                    elif re.search(r'\/core-properties$',rel.Type,flags=re.IGNORECASE):
                        self.corePropertiesPath = self.zipreader.normalizepath(rel.Target)
                    elif re.search(r'\/extended-properties$',rel.Type,flags=re.IGNORECASE):
                        self.extendedPropertiesPath = self.zipreader.normalizepath(rel.Target)
        #
        if self.documentPath:
            self.ok = True
    #
    def close(self):
        if self.zipreader:
            self.zipreader.close()
        self.zipreader = None
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
    def parserelationshipsfile(self,path):
        rels = { }
        #
        xroot = self.readxml(path)
        if xroot == None:
            return None
        #
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
                        rels[nRel.Id] = nRel
        #
        return rels
    #
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
    #
    def registerZIPContentTypeByExtension(self,ext,contenttype,*,ppath="/"):
        ext = ext.lower()
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
        xroot = self.readxml("/[Content_Types].xml")
        if xroot == None:
            return None
        #
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
    def dbg_dump(self):
        print("Debug dump")
        print("  ok="+str(self.ok))
        if self.documentPath:
            print("  documentPath="+str(self.documentPath))
        if self.corePropertiesPath:
            print("  documentPath="+str(self.corePropertiesPath))
        if self.extendedPropertiesPath:
            print("  documentPath="+str(self.extendedPropertiesPath))
        #
        self.dbg_dump_metamap()
    #
    def dbg_dump_metamap(self):
        print("Debug dump zipmetamap")
        for ent in self.zipmetamap:
            print("  "+str(ent)+": "+str(self.zipmetamap[ent]))

zr = OOXMLReader(inFile)
zr.dbg_dump()
zr.close()

