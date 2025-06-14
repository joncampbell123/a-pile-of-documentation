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
                print("Open tag "+hent.tag)
                self.stackNodes[-1].children.append(hent)
                self.stackNodes.append(hent)
                return
            elif hent.tagInfo == 'close':
                print("Close tag "+hent.tag)
                shouldbe = i = len(self.stackNodes) - 1
                while i >= 0:
                    if self.stackNodes[i].elemType == 'tag' and self.stackNodes[i].tagInfo == 'open':
                        if self.stackNodes[i].tag.lower() == hent.tag.lower():
                            break;
                        # some tags are just used in open-only form and it's just expected
                        if self.stackNodes[i].tag.lower() == 'br' or self.stackNodes[i].tag.lower() == 'img' or self.stackNodes[i].tag.lower() == 'option' or self.stackNodes[i].tag.lower() == 'input' or self.stackNodes[i].tag.lower() == 'link' or self.stackNodes[i].tag.lower() == 'meta' or self.stackNodes[i].tag.lower() == 'hr' or self.stackNodes[i].tag.lower() == 'source' or self.stackNodes[i].tag.lower() == 'picture':
                            shouldbe = i - 1
                    i -= 1
                #
                if i < shouldbe:
                    print("WARNING: Closing tag "+hent.tag+" match not at expected place in tag")
                    #
                    skips = ""
                    for j in range(shouldbe,i,-1):
                        if not skips == "":
                            skips += " "
                        skips += self.stackNodes[j].tag
                    print("  Skips: "+skips)
                    #
                    skips = ""
                    for j in range(len(self.stackNodes)-1,-1,-1):
                        if not skips == "":
                            skips += " "
                        skips += self.stackNodes[j].tag
                    print("  Stack: "+skips)
                #
                if i >= 0:
                    self.stackNodes = self.stackNodes[0:i]
                else:
                    print("WARNING: Unable to match closing tag "+hent.tag)
                #
                return
        #
        self.stackNodes[-1].children.append(hent)

hihtmlstate = HTMLhiReaderState()
for ent in HTMLmidParse(rawhtml,hihtmlstate.midstate):
    hihtmlstate.addNode(HTMLhiToken(ent))

