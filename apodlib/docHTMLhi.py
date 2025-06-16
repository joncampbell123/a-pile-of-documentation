
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
        'center': {
            'flags': htmlTagsInfoSameLevelRepeat|htmlTagsInfoUpLevelUnclosedRepeat
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
        'link': htmlTagsInfoNoClose,
        'meta': htmlTagsInfoNoClose,
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
    docType = None
    fixups = [ ]
    rootNode = None
    stackNodes = None
    htmlElement = None
    headElement = None
    bodyElement = None
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
                self.docType = self.parseMode = self.midstate.doctype
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
                return
        #
        self.stackNodes[-1].children.append(hent)

def HTMLhiParseAll(blob,state):
    for ent in HTMLmidParse(blob,state.midstate):
        state.addNode(ent)
    #
    if state.docType == 'html':
        for ent in state.rootNode.children:
            if ent.elemType == 'tag' and ent.tagInfo == 'open':
                if ent.tag.lower() == 'html':
                    state.htmlElement = ent
        #
        if not state.htmlElement == None:
            scanstate = None
            preBody = [ ]
            shouldHead = [ ]
            chl = state.htmlElement.children
            chlf = False
            for enti in range(0,len(chl)):
                ent = chl[enti]
                if ent.elemType == 'tag':
                    if ent.tag.lower() == 'head':
                        if scanstate == None:
                            state.headElement = ent
                            scanstate = 'head'
                            continue
                    #
                    elif ent.tag.lower() == 'body':
                        if scanstate == 'head' or scanstate == None:
                            state.bodyElement = ent
                            scanstate = 'body'
                            continue
                #
                if scanstate == None and state.headElement == None:
                    if ent.elemType == 'tag':
                        if ent.tag.lower() == 'meta' or ent.tag.lower() == 'link' or ent.tag.lower() == 'title':
                            # parsing.html: BODY tag with no HEAD, but HEAD-like tags in the body or before the body
                            shouldHead.append(ent)
                            chl[enti] = None
                            chlf = True
                            continue
                #
                if scanstate == 'head' or scanstate == None:
                    if not chlf:
                        if ent.elemType == 'comment':
                            continue
                        if ent.elemType == 'text':
                            if re.match(r'^[\n\r\t ]+$',ent.text):
                                continue
                    #
                    preBody.append(ent)
                    chl[enti] = None
                    chlf = True
                    continue
            #
            if chlf:
                state.htmlElement.children = list(filter(lambda a: not a == None,state.htmlElement.children))
            #
            if state.bodyElement == None: # test case arabic.html, no BODY tag at all, so make one
                state.fixups.append('noBodyMakeBody')
                #
                fakeBodyTag = HTMLToken()
                fakeBodyTag.elemType = 'tag'
                fakeBodyTag.tagInfo = 'open'
                fakeBodyTag.tag = 'body'
                #
                state.htmlElement.children.append(fakeBodyTag)
                state.bodyElement = fakeBodyTag
            #
            if len(preBody) > 0:
                state.fixups.append('mergePreBodyIntoBody')
                #
                state.bodyElement.children = preBody + state.bodyElement.children
                preBody = [ ]
            #
            if state.headElement == None:
                state.fixups.append('noHeadMakeHead')
                #
                fakeHeadTag = HTMLToken()
                fakeHeadTag.elemType = 'tag'
                fakeHeadTag.tagInfo = 'open'
                fakeHeadTag.tag = 'head'
                #
                state.htmlElement.children = [ fakeHeadTag ] + state.htmlElement.children
                state.headElement = fakeHeadTag
            #
            if len(shouldHead) > 0:
                state.fixups.append('mergeShouldHeadIntoHead')
                #
                state.headElement.children = shouldHead + state.headElement.children
                shouldHead = [ ]

