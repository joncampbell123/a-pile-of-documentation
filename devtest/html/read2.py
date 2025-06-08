#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTML import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

def bin2unicode(v,encoding):
    if encoding == None or encoding == 'binary' or v == None or not isinstance(v, (bytes, bytearray)):
        return v
    return v.decode(encoding,'replace')

def HTMLgetEntity(e):
    if len(e) >= 2 and e[0] == '#':
        if re.match(r'^\#x[a-fA-F0-9]+$',e):
            return chr(int(e[2:],16))
        if re.match(r'^\#[0-9]+$',e):
            return chr(int(e[1:],10))
    return ''

def HTMLdecodeEntities(html):
    i = 0
    r = ''
    while i < len(html):
        p = re.search(r'\&([a-zA-Z0-9\#]+);',html[i:])
        if p:
            beg = p.span()[0]+i
            end = p.span()[1]+i
            if i < beg:
                r += html[i:beg]
            entity = p.groups()[0]
            r += HTMLgetEntity(entity)
            i = end
        else:
            r += html[i:]
            i = len(html)
            break
    return r

class HTMLmidAttr(HTMLllAttr):
    def __init__(self,llattr,encoding):
        super().__init__(llattr)
        self.value = bin2unicode(self.value,encoding)
        self.name = bin2unicode(self.name,encoding)

class HTMLmidToken(HTMLllToken):
    def __init__(self,lltoken,encoding):
        super().__init__(lltoken)
        self.text = bin2unicode(self.text,encoding)
        self.tag = bin2unicode(self.tag,encoding)
        self.attr = map(lambda a: HTMLmidAttr(a,encoding), self.attr)
        if self.elemType == 'text':
            if not self.text == None:
                self.text = HTMLdecodeEntities(self.text)
        elif self.elemType == 'tag':
            if not (self.tag == 'script' or self.tag == 'style'):
                if not self.text == None:
                    self.text = HTMLdecodeEntities(self.text)

class HTMLmidReaderState:
    llstate = None
    initTags = None
    encoding = None # encoding of text presented by the low level state
    doctype = None
    dtd = None
    #
    WAIT_ENCODING = 0
    NORMAL = 1
    def __init__(self):
        self.llstate = HTMLllReaderState()
        self.initTags = [ ]

def HTMLmidGuessEncoding(state):
    if state.doctype == 'html':
        if state.dtd == None:
            return 'utf-8' # anything new enough to use HTML 5 <!DOCTYPE HTML> is probably using UTF-8
    #
    return 'iso-8859-1' # reasonable guess for old HTML files without a DOCTYPE

def HTMLmidParse(blob,state=HTMLmidReaderState()):
    initTags = [ ]
    llit = iter(HTMLllParse(blob,state.llstate))
    for ent in llit:
        initTags.append(ent)
        #
        if not (state.llstate.encoding == None or state.llstate.encoding == 'binary'):
            if not state.llstate.memencoding == None:
                state.encoding = state.llstate.memencoding
            else:
                state.encoding = state.llstate.encoding
            #
            break
        #
        if ent.elemType == 'tag':
            # on <body> opening tag, stop scanning for charset encoding.
            # arabic.html: also stop on </head> because this HTML document doesn't have a <body> tag
            if ent.tagInfo == 'close':
                if ent.tag.lower() == b'head':
                    if state.encoding == None:
                        state.encoding = HTMLmidGuessEncoding(state)
                    break
            elif ent.tagInfo == 'open':
                if ent.tag.lower() == b'body':
                    if state.encoding == None:
                        state.encoding = HTMLmidGuessEncoding(state)
                    break
        #
        elif ent.elemType == 'doctype':
            if state.doctype == None:
                ai = iter(ent.attr)
                try:
                    a = next(ai)
                    if a.name.lower() == b'html':
                        state.doctype = 'html'
                        a = next(ai)
                        if a.name.lower() == b'public': # PUBLIC "-HTMLblahblah"
                            a = next(ai)
                            if a.name == None and not a.value == None:
                                state.dtd = a.value.decode('iso-8859-1')
                except StopIteration:
                    True
        #
        elif ent.elemType == 'procinst':
            if ent.tag.lower() == b'xml':
                if state.doctype == None:
                    state.doctype = 'xml'
    #
    for ent in initTags:
        yield HTMLmidToken(ent,state.encoding)
    #
    for ent in llit:
        yield HTMLmidToken(ent,state.encoding)

midhtmlstate = HTMLmidReaderState()
for ent in HTMLmidParse(rawhtml,midhtmlstate):
    print(ent)

print("Encoding: "+str(midhtmlstate.encoding))
print("Doctype: "+str(midhtmlstate.doctype))
print("Doctype DTD: "+str(midhtmlstate.dtd))
