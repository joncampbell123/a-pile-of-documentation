
import os
import re
import sys

from apodlib.docHTMLmid import *

htmlTagsInfoNoClose = 0x01
htmlTagsInfoSameLevelRepeat = 0x02

htmlTagsInfo = {
        'br': htmlTagsInfoNoClose,
        'img': htmlTagsInfoNoClose,
        'input': htmlTagsInfoNoClose,
        'meta': htmlTagsInfoSameLevelRepeat,
        'option': htmlTagsInfoSameLevelRepeat,
        'p': htmlTagsInfoSameLevelRepeat
}

class HTMLhiAttr(HTMLmidAttr):
    def __init__(self,midattr=HTMLmidAttr()):
        super().__init__(midattr)
    def __str__(self):
        return super().__str__()

class HTMLhiToken(HTMLmidToken):
    children = None
    def __init__(self,midtoken=HTMLmidToken()):
        super().__init__(midtoken)
        self.attr = list(map(lambda a: HTMLhiAttr(a), self.attr))
        self.children = [ ]
    def __str__(self):
        return super().__str__()

class HTMLhiReaderState:
    global htmlTagsNoClosing
    parseMode = None
    midstate = None
    rootNode = None
    stackNodes = None
    def __init__(self):
        self.midstate = HTMLmidReaderState()
        self.rootNode = HTMLhiToken()
        self.rootNode.tag = 'root'
        self.rootNode.elemType = 'root'
        self.stackNodes = [ self.rootNode ]
    def getRoot(self):
        return self.rootNode
    def addNode(self,ment):
        if len(self.stackNodes) == 0:
            return
        #
        hent = HTMLhiToken(ment) #HTMLmidToken to HTMLhiToken
        #
        if self.parseMode == None:
            if self.midstate.doctype == 'html' or self.midstate.doctype == 'xml':
                self.parseMode = self.midstate.doctype
        #
        if hent.elemType == 'tag':
            if hent.tagInfo == 'open':
                if hent.tag.lower() == 'html' or self.parseMode == None:
                    self.parseMode = 'html'
                #
                if self.parseMode == 'html':
                    if hent.tag.lower() in htmlTagsInfo:
                        nfo = htmlTagsInfo[hent.tag.lower()]
                        if (nfo & htmlTagsInfoNoClose):
                            self.stackNodes[-1].children.append(hent)
                            return
                        if (nfo & htmlTagsInfoSameLevelRepeat):
                            if hent.tag.lower() == self.stackNodes[-1].tag.lower():
                                self.stackNodes[-1].children.append(hent)
                                return
                #
                self.stackNodes[-1].children.append(hent)
                self.stackNodes.append(hent)
                return
            elif hent.tagInfo == 'close':
                i = len(self.stackNodes) - 1
                while i >= 0:
                    if self.stackNodes[i].elemType == 'tag' and self.stackNodes[i].tagInfo == 'open':
                        if self.stackNodes[i].tag.lower() == hent.tag.lower():
                            break;
                    #
                    i -= 1
                #
                if i >= 0:
                    self.stackNodes = self.stackNodes[0:i]
                #
                if hent.tag == 'htnl' and self.parseMode == 'html':
                    self.parseMode = None
                #
                return
        #
        self.stackNodes[-1].children.append(hent)

def HTMLhiParse(blob,state):
    for ent in HTMLmidParse(blob,state.midstate):
        yield HTMLhiToken(ent)

def HTMLhiParseAll(blob,state):
    for ent in HTMLhiParse(blob,state):
        state.addNode(ent)

