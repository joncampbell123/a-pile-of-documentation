#!/usr/bin/python3

import os
import re
import sys

def rawhtmlloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTML import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

class HTMLmidReaderState:
    llstate = None
    initTags = None
    encoding = None
    doctype = None
    state = None
    dtd = None
    #
    WAIT_ENCODING = 0
    NORMAL = 1
    def __init__(self):
        self.llstate = HTMLllReaderState()
        self.state = self.WAIT_ENCODING
        self.initTags = [ ]

def HTMLmidGuessEncoding(state):
    if state.doctype == 'html':
        if state.dtd == None:
            return 'utf-8' # anything new enough to use HTML 5 <!DOCTYPE HTML> is probably using UTF-8
    #
    return 'iso-8859-1' # reasonable guess for old HTML files without a DOCTYPE

midhtmlstate = HTMLmidReaderState()

for ent in HTMLllParse(rawhtml,midhtmlstate.llstate):
    midhtmlstate.initTags.append(ent)
    if ent.elemType == 'tag':
        # on <body> opening tag, stop scanning for charset encoding.
        # arabic.html: also stop on </head> because this HTML document doesn't have a <body> tag
        if ent.tagInfo == 'close':
            if ent.tag.lower() == b'head':
                if midhtmlstate.encoding == None:
                    midhtmlstate.encoding = HTMLmidGuessEncoding(midhtmlstate)
                break
        elif ent.tagInfo == 'open':
            if ent.tag.lower() == b'body':
                if midhtmlstate.encoding == None:
                    midhtmlstate.encoding = HTMLmidGuessEncoding(midhtmlstate)
                break
    elif ent.elemType == 'doctype':
        if midhtmlstate.doctype == None:
            ai = iter(ent.attr)
            try:
                a = next(ai)
                if a.name.lower() == b'html':
                    midhtmlstate.doctype = 'html'
                    a = next(ai)
                    if a.name.lower() == b'public': # PUBLIC "-HTMLblahblah"
                        a = next(ai)
                        if a.name == None and not a.value == None:
                            midhtmlstate.dtd = a.value.decode('iso-8859-1')
            except StopIteration:
                True
    elif ent.elemType == 'procinst':
        if ent.tag.lower() == b'xml':
            if midhtmlstate.doctype == None:
                midhtmlstate.doctype = 'xml'
    if not (midhtmlstate.llstate.encoding == None or midhtmlstate.llstate.encoding == 'binary'):
        midhtmlstate.encoding = midhtmlstate.llstate.encoding
        break

print("Encoding: "+str(midhtmlstate.encoding))
print("Doctype: "+str(midhtmlstate.doctype))
print("Doctype DTD: "+str(midhtmlstate.dtd))
