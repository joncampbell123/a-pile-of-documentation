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

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

# low level reader:
# returns a flat sequence of HTML tags, or text.
# concerns itself only with whether the text is UTF-16 or not.
# it's up to you to turn the stream of tags into a DOM hierarchy and convert from whatever charset to UTF-8.

UTF16LE_BOM = bytearray([0xFF, 0xFE])
UTF16BE_BOM = bytearray([0xFE, 0xFF])
UTF8_BOM = bytearray([0xEF, 0xBB, 0xBF])
UTF16LE_XMLDECL = bytearray([0x3C, 0x00, 0x3F, 0x00, 0x78, 0x00])
UTF16BE_XMLDECL = bytearray([0x00, 0x3C, 0x00, 0x3F, 0x00, 0x78])

class HTMLllReaderState:
    encoding = None # 'binary' 'utf8' 'utf16le' 'utf16be'
    def __init__(self):
        self.encoding = None

def HTMLwhitespace(c):
    return c == 0x09 or c == 0x0A or c == 0x0C or c == 0x0D or c == 0x20

def HTMLllParse(blob,state=HTMLllReaderState()):
    i = 0
    if state.encoding == None:
        if len(blob) >= 2:
            if blob[0:2] == UTF16LE_BOM:
                state.encoding = 'utf16le'
                i = 2
            elif blob[0:2] == UTF16BE_BOM:
                state.encoding = 'utf16be'
                i = 2
        if state.encoding == None:
            if len(blob) >= 3:
                if blob[0:3] == UTF8_BOM:
                    state.encoding = 'utf8'
                    i = 3
        if state.encoding == None:
            if len(blob) >= 6:
                if blob[0:6] == UTF16LE_XMLDECL:
                    state.encoding = 'utf16le'
                if blob[0:6] == UTF16BE_XMLDECL:
                    state.encoding = 'utf16be'
        if state.encoding == None:
            state.encoding = 'binary'
    #
    if state.encoding == 'utf16le':
        blob = blob[i:].decode('utf-16le').encode('utf-8')
        i = 0
    elif state.encoding == 'utf16be':
        blob = blob[i:].decode('utf-16be').encode('utf-8')
        i = 0
    #
    print(blob)

llhtmlstate = HTMLllReaderState()
llhtml = HTMLllParse(rawhtml,llhtmlstate)

