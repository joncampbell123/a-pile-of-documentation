#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLmid import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

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
        if hent.elemType == 'tag':
            if hent.tagInfo == 'open':
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
                return
        #
        self.stackNodes[-1].children.append(hent)

def HTMLhiParse(blob,state):
    for ent in HTMLmidParse(blob,state.midstate):
        yield HTMLhiToken(ent)

def HTMLhiParseAll(blob,state):
    for ent in HTMLhiParse(blob,state):
        state.addNode(ent)

hihtmlstate = HTMLhiReaderState()
HTMLhiParseAll(rawhtml,hihtmlstate)

