
import os
import re
import sys

from apodlib.docHTMLmid import *

htmlTagsInfoNoClose = 0x01
htmlTagsInfoSameLevelRepeat = 0x02
htmlTagsInfoUpLevelUnclosedRepeat = 0x04

# ancient HTML rules regarding <A>
# does it open a tag? <A HREF="...">link</A>
# or does it just stand alone? <A NAME="something">
# These are the arcane rules of Web 1.0.
def HTMLAnchorFlagTest(h):
    hasName = False
    hasHREF = False
    #
    for attr in h.attr:
        if not attr.name == None:
            if attr.name.lower() == "href":
                hasHREF = True
            elif attr.name.lower() == "name":
                hasName = True
    # has HREF? definitely open
    if hasHREF:
        return 0
    # has name? Stands alone
    if hasName:
        return htmlTagsInfoNoClose
    # If we don't know, assume it opens
    return 0 # return flags

htmlTagsInfo = {
        'a': {
            'flagfunction': HTMLAnchorFlagTest
        },
        'dd': {
            'flags': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
            'also closes': [ 'dt' ]
        },
        'dl': {
            'flags': htmlTagsInfoSameLevelRepeat,
            'also closes': [ 'dt', 'dd' ]
        },
        'dt': {
            'flags': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
            'also closes': [ 'dd' ]
        },
        'br': htmlTagsInfoNoClose,
        'hr': {
            'flags': htmlTagsInfoNoClose,
            'also closes': [ 'p' ]
        },
        'img': htmlTagsInfoNoClose,
        'input': htmlTagsInfoNoClose,
        'li': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
        'link': htmlTagsInfoSameLevelRepeat,
        'meta': htmlTagsInfoSameLevelRepeat,
        'option': htmlTagsInfoSameLevelRepeat,
        'p': htmlTagsInfoSameLevelRepeat,
        'source': htmlTagsInfoNoClose,
        'td': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
        'tr': {
            'flags': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
            'also closes': [ 'td' ]
        },
        'th': {
            'flags': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat,
            'also closes': [ 'td' ]
        },
        'ul': {
            'also closes': [ 'li' ]
        },
        'ol': {
            'also closes': [ 'li' ]
        }
}

class HTMLhiReaderState:
    global htmlTagsNoClosing
    parseMode = None
    midstate = None
    rootNode = None
    stackNodes = None
    def __init__(self):
        self.midstate = HTMLmidReaderState()
        self.rootNode = HTMLToken()
        self.rootNode.tag = 'root'
        self.rootNode.elemType = 'root'
        self.stackNodes = [ self.rootNode ]
    def getRoot(self):
        return self.rootNode
    def addNode(self,hent):
        if len(self.stackNodes) == 0:
            return
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
                        if isinstance(nfo,dict):
                            if 'also closes' in nfo:
                                cut = len(self.stackNodes)
                                i = cut - 1
                                while i >= 0:
                                    if self.stackNodes[i].elemType == 'tag' and self.stackNodes[i].tagInfo == 'open':
                                        if self.stackNodes[i].tag.lower() == hent.tag.lower():
                                            break;
                                        ii = list(filter(lambda a: a.lower() == self.stackNodes[i].tag.lower(),nfo['also closes']))
                                        if len(ii) > 0:
                                            cut = i
                                    #
                                    i -= 1
                                #
                                if cut >= 0:
                                    self.stackNodes = self.stackNodes[0:cut]
                                #
                            if 'flagfunction' in nfo:
                                nfo = nfo['flagfunction'](hent)
                            elif 'flags' in nfo:
                                nfo = nfo['flags']
                            else:
                                nfo = 0
                        #
                        if (nfo & htmlTagsInfoNoClose):
                            self.stackNodes[-1].children.append(hent)
                            return
                        if (nfo & htmlTagsInfoSameLevelRepeat):
                            if hent.tag.lower() == self.stackNodes[-1].tag.lower():
                                self.stackNodes = self.stackNodes[0:len(self.stackNodes)-1]
                                self.stackNodes[-1].children.append(hent)
                                self.stackNodes.append(hent)
                                return
                        if (nfo & htmlTagsInfoUpLevelUnclosedRepeat):
                            i = len(self.stackNodes) - 2 # already checked same!
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
                            self.stackNodes[-1].children.append(hent)
                            self.stackNodes.append(hent)
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

def HTMLhiParseAll(blob,state):
    for ent in HTMLmidParse(blob,state.midstate):
        state.addNode(ent)

