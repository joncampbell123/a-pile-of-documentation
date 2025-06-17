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
    r = re.match(r'[ \t\n\r\f]+',blob[i:])
    if r:
        return r.span()[1]+i
    else:
        return i

def CSSllishexdigit(c):
    if ord(c) >= ord('0') and ord(c) <= ord('9'):
        return ord(c) - ord('0')
    #
    if ord(c) >= ord('a') and ord(c) <= ord('f'):
        return ord(c) + 10 - ord('a')
    #
    if ord(c) >= ord('A') and ord(c) <= ord('F'):
        return ord(c) + 10 - ord('A')
    #
    return None

def CSSllidentescapereadchar(blob,i,first):
    if i < len(blob):
        if blob[i] == '\\':
            if i >= len(blob):
                return [i,None]
            #
            i += 1
            hv = CSSllishexdigit(blob[i])
            if not hv == None:
                fv = hv
                i += 1
                count = 1
                while True:
                    hv = CSSllishexdigit(blob[i])
                    if hv == None:
                        break
                    fv = (fv << 4) + hv
                    i += 1
                    count += 1
                    if count >= 6:
                        break
                return [i,chr(fv)]
            else:
                v = blob[i]
                i += 1
                return [i,v]
        elif re.match(r'[a-zA-Z_]',blob[i]) or (not first and re.match(r'[0-9]',blob[i])) or ord(blob[i]) >= 0x80:
            v = blob[i]
            i += 1
            return [i,v]
    #
    return [i,None]

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
        r = re.match(r'^(\\|-{0,1}[a-zA-Z_\u0080-\uFFFFFF\\]|--[a-zA-Z0-9_\u0080-\uFFFFFF\\])',blob[i:])
        if r:
            t = CSSllToken()
            t.token = 'ident'
            t.text = ''
            #
            first = True
            if blob[i:i+2] == '--':
                t.text += '--'
                first = False
                i += 2
            elif blob[i] == '-':
                t.text += '-'
                i += 1
            #
            while True:
                [i,cc] = CSSllidentescapereadchar(blob,i,first)
                if cc == None:
                    break
                t.text += cc
                first = False
            #
            yield t
            continue
        #
        t = CSSllToken()
        t.token = 'char'
        t.text = blob[i]
        i += 1
        yield t
        continue

state = CSSllState()

for ent in CSSllparse(rawcss,state):
    print(ent)

