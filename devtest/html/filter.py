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

def HTMLllTokenToHTML(ent):
    if ent.elemType == 'text':
        if not ent.text == None:
            return ent.text
    if ent.elemType == 'comment':
        if not ent.text == None:
            return b'<!--'+ent.text+b'-->'
    if ent.elemType == 'doctype':
        r = b'<!'
        if not ent.tag == None:
            r += ent.tag
        #
        for a in ent.attr:
            r += b' '
            if not a.name == None:
                r += a.name
                if not a.value == None:
                    r += b'='
            #
            if not a.value == None:
                r += b'"'+a.value+b'"'
        #
        r += b'>'
        return r
    if ent.elemType == 'tag':
        if ent.tagInfo == 'close':
            r = b'</'
        else:
            r = b'<'
        #
        if not ent.tag == None:
            r += ent.tag
        #
        for a in ent.attr:
            r += b' '
            if not a.name == None:
                r += a.name
                if not a.value == None:
                    r += b'='
            #
            if not a.value == None:
                r += b'"'+a.value+b'"'
        #
        if ent.tagInfo == 'self':
            r += b'/>'
        else:
            r += b'>'
        #
        return r
    #
    return b''

llhtmlstate = HTMLllReaderState()

sys.stdout.buffer.flush()
for ent in HTMLllParse(rawhtml,llhtmlstate):
    sys.stdout.buffer.write(HTMLllTokenToHTML(ent))

