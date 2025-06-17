#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docBOM import *

# low level reader:
# returns a flat sequence of HTML tags, or text.
# concerns itself only with whether the text is UTF-16 or not.
# it's up to you to turn the stream of tags into a DOM hierarchy and convert from whatever charset to UTF-8.

def rawcssloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

class CSSllToken:
    token = None
    text = None
    #
    def __init__(self):
        True
    def __str__(self):
        r = "[CSSllToken"
        if not self.token == None:
            r += " token="+str(self.token)
        if not self.text == None:
            r += " text="+str(self.text)
        r += "]"
        return r

class CSSllState:
    encoding = None

inFile = sys.argv[1]
rawcss = rawcssloadfile(inFile)

def CSSskipwhitespace(blob,i):
    r = re.search(r'[ \t\n\r\f]+',blob[i:])
    if r:
        return r.span()[1]+i
    else:
        return i

def CSSllparse(blob,state=CSSllState()):
    i = 0
    # NTS: You should set encoding to the value given from the HTML parser, if possible
    if state.encoding == None:
        state.encoding = "utf-8"
    #
    blob = blob.decode(state.encoding)
    #
    while i < len(blob):
        i = CSSskipwhitespace(blob,i)
        if i >= len(blob):
            break
        #
        if blob[i:i+2] == '/*':
            begin = i+2
            r = re.search(r'\*\/',blob[begin:])
            if r:
                end = r.span()[0]+begin
                i = r.span()[1]+begin
            else:
                i = end = len(blob)
            #
            t = CSSllToken()
            t.token = 'comment'
            t.text = blob[begin:end]
            yield t
            continue
        #
        r = re.match(r'^((-{0,1}[a-zA-Z_\u0080-\uFFFFFF]|--[a-zA-Z0-9_\u0080-\uFFFFFF])[a-zA-Z0-9_\u0080-\uFFFFFF]*)',blob[i:])
        if r:
            begin = r.span()[0]+i
            end = r.span()[1]+i
            i = end
            #
            t = CSSllToken()
            t.token = 'ident'
            t.text = blob[begin:end]
            yield t
            continue
        #
        break

state = CSSllState()

for ent in CSSllparse(rawcss,state):
    print(ent)

