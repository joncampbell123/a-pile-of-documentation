
import os
import re
import sys

from apodlib.docBOM import *

# low level reader:
# returns a flat sequence of HTML tags, or text.
# concerns itself only with whether the text is UTF-16 or not.
# it's up to you to turn the stream of tags into a DOM hierarchy and convert from whatever charset to UTF-8.

def rawhtmlloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

class HTMLllReaderState:
    encoding = None # 'binary' 'utf8' 'utf16le' 'utf16be'
    memencoding = None # encoding stored in memory
    taglock = None # None 'script' 'style' because HTML tag parsing must be restricted within these tags
    inForm = None # None 'html' 'xml'

class HTMLllAttr:
    name = None
    value = None
    offset = None # byte offset in data this occurred
    def __init__(self,what=None):
        if not what == None:
            self.name = what.name
            self.value = what.value
            self.offset = what.offset
    def __str__(self):
        r = '['+type(self).__name__
        if not self.name == None:
            r += ' name='+str(self.name)
        if not self.value == None:
            r += ' value='+str(self.value)
        if not self.offset == None:
            r += ' offset='+str(self.offset)
        r += ']'
        return r

class HTMLllToken:
    elemType = None # 'text' 'comment' <!-- --> 'tag' <tag> </tag> <tag/> 'procinst' <? 'doctype' <!
    tagInfo = None # 'open' 'close' 'self'
    text = None
    tag = None
    attr = None
    offset = None # byte offset in data this occurred
    def __init__(self,what=None):
        self.attr = [ ]
        if not what == None:
            self.elemType = what.elemType
            self.tagInfo = what.tagInfo
            self.text = what.text
            self.tag = what.tag
            self.attr = what.attr.copy()
            self.offset = what.offset
    def __str__(self):
        r = '['+type(self).__name__
        if not self.elemType == None:
            r += ' elemType='+str(self.elemType)
        if not self.tagInfo == None:
            r += ' tagInfo='+str(self.tagInfo)
        if not self.tag == None:
            r += ' tag='+str(self.tag)
        if not self.text == None:
            r += ' text='+str(self.text)
        if not self.offset == None:
            r += ' offset='+str(self.offset)
        for a in self.attr:
            r += ' attr='+str(a)
        r += ']'
        return r

def HTMLllwhitespace(c):
    return c == 0x09 or c == 0x0A or c == 0x0C or c == 0x0D or c == 0x20

def HTMLllskipwhitespace(line,end):
    if end >= len(line):
        return end
    #
    ei = re.match(b'[\x09\x0A\x0C\x0D\x20]+',line[end:])
    if ei:
        return end+ei.span()[1]
    else:
        return end

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
        state.memencoding = 'utf-8'
        i = 0
    elif state.encoding == 'utf16be':
        blob = blob[i:].decode('utf-16be').encode('utf-8')
        state.memencoding = 'utf-8'
        i = 0
    elif state.encoding == 'utf8':
        state.memencoding = 'utf-8'
    #
    while i < len(blob):
        if state.taglock == 'script':
            p = re.search(b'(\<\/script)',blob[i:])
        elif state.taglock == 'style':
            p = re.search(b'(\<\/style)',blob[i:])
        else:
            p = re.search(b'(\<\!\-\-|\<\!|\<\?|\<\/|\<[a-zA-Z])',blob[i:])
        #
        if p:
            what = p.groups()[0]
            at = p.span()[0] + i
            # HTML text
            if i < at:
                ent = HTMLllToken()
                ent.elemType = 'text'
                ent.text = blob[i:at]
                ent.offset = i
                yield ent
            #
            begin = i = at + len(what)
            #
            if what == b"</script" or what == b"</style":
                what = b"</"
                begin = i = at + 2
            #
            if what == b'<!--':
                end = blob.find(b'-->',i)
                if end >= 0:
                    i = end + 3
                else:
                    i = end = len(blob)
                #
                ent = HTMLllToken()
                ent.elemType = 'comment'
                ent.offset = begin
                ent.text = blob[begin:end]
                yield ent
            else:
                allowAttr = True
                ent = HTMLllToken()
                ent.offset = at
                if what == b'<!':
                    ent.elemType = 'doctype'
                elif what == b'<?':
                    ent.elemType = 'procinst'
                elif what == b'</':
                    allowAttr = False
                    ent.elemType = 'tag'
                    ent.tagInfo = 'close'
                else:
                    begin = i = at + 1
                    ent.elemType = 'tag'
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
                            nva.offset = i
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
                                    while i < len(blob) and not blob[i] == match:
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
                        elif blob[i] == ord('\"') or blob[i] == ord('\''):
                            nva = HTMLllAttr()
                            nva.offset = i
                            nva.value = b''
                            #
                            match = blob[i]
                            i += 1
                            while i < len(blob) and not blob[i] == match:
                                nva.value += blob[i:i+1]
                                i += 1
                            #
                            if blob[i] == match:
                                i += 1
                            #
                            ent.attr.append(nva)
                        else:
                            while i < len(blob) and not HTMLllwhitespace(blob[i]) and not blob[i] == ord('/') and not blob[i] == ord('>'):
                                i += 1
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
                state.taglock = None
                if ent.elemType == 'tag':
                    if ent.tagInfo == 'open':
                        if state.inForm == 'html':
                            # <script> needs special processing not to misinterpret js as HTML because wrapping it in <!-- --> is so 1990s apparently.
                            if ent.tag.lower() == b'script':
                                state.taglock = 'script'
                            # <style> should be handled specially too so CSS doesn't get confused with HTML
                            if ent.tag.lower() == b'style':
                                state.taglock = 'style'
                            # we would like to know the encoding
                            if ent.tag.lower() == b'meta':
                                charset = None
                                content = None
                                httpequiv = None
                                for a in ent.attr:
                                    if a.name.lower() == b'charset':
                                        if charset == None:
                                            charset = a.value
                                    elif a.name.lower() == b'http-equiv':
                                        if httpequiv == None:
                                            httpequiv = a.value
                                    elif a.name.lower() == b'content':
                                        if content == None:
                                            content = a.value
                                #
                                if (state.encoding == None or state.encoding == 'binary') and state.memencoding == None:
                                    if not charset == None:
                                        state.encoding = charset.decode('iso-8859-1').lower()
                                    elif not httpequiv == None and httpequiv.lower() == b'content-type' and not content == None:
                                        x = list(re.split(b'; *',content))
                                        if len(x) > 0 and x[0].lower() == b'text/html':
                                            x = x[1:]
                                            for xem in x:
                                                xi = xem.find(ord('='))
                                                if xi >= 0:
                                                    name = xem[0:xi]
                                                    value = xem[xi+1:]
                                                else:
                                                    name = xem
                                                    value = ''
                                                #
                                                if name.lower() == b'charset':
                                                    if len(value) > 0:
                                                        state.encoding = value.decode('iso-8859-1').lower()
                        elif state.inForm == None:
                            if ent.tag.lower() == b'html':
                                state.inForm = 'html'
                    elif ent.tagInfo == 'close':
                        if state.inForm == 'html':
                            if ent.tag.lower() == b'html':
                                state.inForm = None
                elif ent.elemType == 'procinst':
                    if state.inForm == None:
                        if ent.tag.lower() == b'xml' or ent.tag.lower() == b'xml-stylesheet':
                            state.inForm = ent.tag.lower().decode('ascii')
                            # some XML documents specify the encoding in this tag
                            for a in ent.attr:
                                if a.name.lower() == b'encoding':
                                    if state.encoding == None or state.encoding == 'binary' and not a.value == None:
                                        state.encoding = a.value.decode('iso-8859-1').lower()
                #
                yield ent
            #
        else:
            # HTML text
            ent = HTMLllToken()
            ent.elemType = 'text'
            ent.text = blob[i:]
            ent.offset = i
            yield ent
            break

def HTMLllTokenToHTML(ent,state=HTMLllReaderState()):
    if state.encoding == 'utf16be':
        encfunc = lambda x : x.decode('utf-8').encode('utf-16be')
    elif state.encoding == 'utf16le':
        encfunc = lambda x : x.decode('utf-8').encode('utf-16le')
    else:
        encfunc = lambda x : x
    #
    if ent.elemType == 'text':
        if not ent.text == None:
            return encfunc(ent.text)
    if ent.elemType == 'comment':
        if not ent.text == None:
            return encfunc(b'<!--'+ent.text+b'-->')
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
        return encfunc(r)
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
        return encfunc(r)
    #
    return b''

