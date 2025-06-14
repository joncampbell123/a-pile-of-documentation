
import os
import re
import sys

from apodlib.docHTML import *
from apodlib.docHTMLentities import *

def HTMLAttrllToMidIP(attr,encoding=None):
    if not encoding == None:
        attr.value = HTMLbin2unicode(attr.value,encoding)
        attr.name = HTMLbin2unicode(attr.name,encoding)
    #
    return attr

def HTMLTokenllToMidIP(tok,encoding=None):
    if not encoding == None:
        tok.text = HTMLbin2unicode(tok.text,encoding)
        tok.tag = HTMLbin2unicode(tok.tag,encoding)
        tok.attr = list(map(lambda a: HTMLAttrllToMidIP(a,encoding), tok.attr))
        #
        if tok.elemType == 'text':
            if not tok.text == None:
                tok.text = HTMLdecodeEntities(tok.text)
        elif tok.elemType == 'tag':
            if not (tok.tag == 'script' or tok.tag == 'style'):
                if not tok.text == None:
                    tok.text = HTMLdecodeEntities(tok.text)
    #
    return tok

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

def HTMLbin2unicode(v,encoding):
    if v == None or not isinstance(v, (bytes, bytearray)):
        return v
    if encoding == None or encoding == 'binary':
        return v.decode('iso-8859-1','replace')
    return v.decode(encoding,'replace')

def HTMLgetEntity(e):
    if len(e) >= 2 and e[0] == '#':
        if re.match(r'^\#x[a-fA-F0-9]+$',e):
            return chr(int(e[2:],16))
        if re.match(r'^\#[0-9]+$',e):
            return chr(int(e[1:],10))
    #
    if e in HTMLent2u:
        return HTMLent2u[e]
    #
    return '&'+e+';' # most browsers seem to just not replace it at all

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

def HTMLmidGuessEncoding(state):
    if state.doctype == 'html':
        if state.dtd == None:
            return 'utf-8' # anything new enough to use HTML 5 <!DOCTYPE HTML> is probably using UTF-8
    #
    if state.doctype == 'xml' or state.doctype == 'xml-stylesheet':
        return 'utf-8' # XML these days is likely UTF-8
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
            if ent.tag.lower() == b'xml' or ent.tag.lower() == b'xml-stylesheet':
                if state.doctype == None:
                    state.doctype = ent.tag.lower().decode('ascii')
                    if state.encoding == None:
                        state.encoding = HTMLmidGuessEncoding(state)
                    break
    #
    for ent in initTags:
        yield HTMLTokenllToMidIP(ent,state.encoding)
    #
    for ent in llit:
        yield HTMLTokenllToMidIP(ent,state.encoding)

