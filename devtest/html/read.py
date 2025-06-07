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

class HTMLllAttr:
    name = None
    value = None
    def __str__(self):
        r = '[HTMLllAttr'
        if not self.name == None:
            r += ' name='+str(self.name)
        if not self.value == None:
            r += ' value='+str(self.value)
        r += ']'
        return r

class HTMLllToken:
    elemType = None # 'text' 'comment' <!-- --> 'tag' <tag> </tag> <tag/> 'procinst' <? 'doctype' <!
    tagInfo = None # 'open' 'close' 'self'
    text = None
    tag = None
    attr = None
    def __init__(self):
        self.attr = [ ]
    def __str__(self):
        r = '[HTMLllToken'
        if not self.elemType == None:
            r += ' elemType='+str(self.elemType)
        if not self.tagInfo == None:
            r += ' tagInfo='+str(self.tagInfo)
        if not self.tag == None:
            r += ' tag='+str(self.tag)
        if not self.text == None:
            r += ' text='+str(self.text)
        for a in self.attr:
            r += ' attr='+str(a)
        r += ']'
        return r

def HTMLllwhitespace(c):
    return c == 0x09 or c == 0x0A or c == 0x0C or c == 0x0D or c == 0x20

def HTMLllskipwhitespace(line,end):
    if end >= len(line):
        return end
    if not line[end] == ord(' '):
        return end
    #
    ei = re.search(b'[\x09\x0A\0x0C\x0D\x20]+',line[end:])
    if ei:
        return end+ei.span()[1]
    else:
        return len(line)

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
    while i < len(blob):
        p = re.search(b'(\<\!\-\-|\<\!|\<\/|\<\?|\<)',blob[i:])
        if p:
            what = p.groups()[0]
            at = p.span()[0] + i
            # HTML text
            if i < at:
                ent = HTMLllToken()
                ent.elemType = 'text'
                ent.text = blob[i:at]
                yield ent
            #
            begin = i = at + len(what)
            if what == b'<!--':
                end = blob.find(b'-->',i)
                if end >= 0:
                    i = end + 3
                else:
                    i = end = len(blob)
                #
                ent = HTMLllToken()
                ent.elemType = 'comment'
                ent.text = blob[begin:end]
                yield ent
            else:
                allowAttr = True
                ent = HTMLllToken()
                if what == b'<!':
                    ent.elemType = 'doctype'
                elif what == b'<?':
                    ent.elemType = 'procinst'
                else:
                    ent.elemType = 'tag'
                    if what == b'</':
                        ent.tagInfo = 'close'
                        allowAttr = False
                    else:
                        ent.tagInfo = 'open'
                #
                if i < len(blob):
                    i = HTMLllskipwhitespace(blob,i)
                    if re.match(b'[a-zA-Z0-9]',blob[i:i+1]):
                        tag = b''
                        while i < len(blob) and not HTMLllwhitespace(blob[i]) and not blob[i] == ord('/') and not blob[i] == ord('>'):
                            tag += blob[i:i+1]
                            i += 1
                        ent.tag = tag
                        i = HTMLllskipwhitespace(blob,i)
                #
                if allowAttr:
                    while i < len(blob):
                        i = HTMLllskipwhitespace(blob,i)
                        if i >= len(blob):
                            break
                        if blob[i] == ord('>'):
                            break
                        if blob[i] == ord('/'):
                            allowAttr = False
                            if ent.tagInfo == 'open':
                                ent.tagInfo = 'self'
                            break
                        #
                        if re.match(b'[a-zA-Z0-9]',blob[i:i+1]):
                            nva = HTMLllAttr()
                            nva.name = b''
                            #
                            while i < len(blob) and not HTMLllwhitespace(blob[i]) and not blob[i] == ord('/') and not blob[i] == ord('>') and not blob[i] == ord('='):
                                nva.name += blob[i:i+1]
                                i += 1
                            #
                            i = HTMLllskipwhitespace(blob,i)
                            if i < len(blob) and blob[i] == ord('='):
                                i += 1
                                nva.value = b''
                                i = HTMLllskipwhitespace(blob,i)
                                if blob[i] == ord('\"') or blob[i] == ord('\''):
                                    match = blob[i]
                                    i += 1
                                    while i < len(blob) and not HTMLllwhitespace(blob[i]) and not blob[i] == match:
                                        nva.value += blob[i:i+1]
                                        i += 1
                                    #
                                    if blob[i] == match:
                                        i += 1
                                else:
                                    while i < len(blob) and not HTMLllwhitespace(blob[i]) and not blob[i] == ord('/') and not blob[i] == ord('>'):
                                        nva.value += blob[i:i+1]
                                        i += 1
                            #
                            ent.attr.append(nva)
                        else:
                            allowAttr = False
                            break
                #
                i = HTMLllskipwhitespace(blob,i)
                while i < len(blob):
                    if blob[i] == ord('>'):
                        i += 1
                        break
                    else:
                        i += 1
                        i = HTMLllskipwhitespace(blob,i)
                #
                yield ent
            #
        else:
            # HTML text
            ent = HTMLllToken()
            ent.elemType = 'text'
            ent.text = blob[i:]
            yield ent
            break

llhtmlstate = HTMLllReaderState()
for ent in HTMLllParse(rawhtml,llhtmlstate):
    print(ent)

