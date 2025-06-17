
import os
import re
import sys

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
    value = None
    text = None
    #
    def __init__(self):
        True
    def __str__(self):
        r = "[CSSllToken"
        if not self.token == None:
            r += " token="+str(self.token)
        if not self.value == None:
            r += " value="+str(self.value)
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

def CSSllescapereadchar(blob,i):
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
        #
        if (i+2) <= len(blob) and blob[i] == '\r' and blob[i+1] == '\n':
            i += 2
        elif blob[i] == ' ' or blob[i] == '\r' or blob[i] == '\n' or blob[i] == '\t' or blob[i] == '\f': # if a space terminates the hex code, it is not left in the buffer as part of the text
            i += 1
        #
        return [i,chr(fv)]
    else:
        v = blob[i]
        i += 1
        return [i,v]

def CSSllidentescapereadchar(blob,i,first):
    if i < len(blob):
        if blob[i] == '\\':
            if i >= len(blob):
                return [i,None]
            #
            i += 1
            return CSSllescapereadchar(blob,i)
        elif re.match(r'[a-zA-Z_]',blob[i]) or (not first and re.match(r'[0-9\-]',blob[i])) or ord(blob[i]) >= 0x80:
            v = blob[i]
            i += 1
            return [i,v]
    #
    return [i,None]

def CSSllIsNumber(blob,i):
    return re.match(r'^[+-]?([0-9]*\.[0-9]+|[0-9]+)([eE][+-]?[0-9]+)?',blob[i:])

def CSSllIsIdentifier(blob,i):
    return re.match(r'^(\\|-{0,1}[a-zA-Z_\u0080-\uFFFFFF\\]|--[a-zA-Z0-9_\u0080-\uFFFFFF\\])',blob[i:])

def CSSllParseIdentifier(r,blob,i):
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
    return [i,t]

def CSSllIsHash(blob,i):
    return re.match(r'^\#([a-zA-Z0-9_\u0080-\uFFFFFF\\\-])',blob[i:])

def CSSllParseHash(r,blob,i):
    t = CSSllToken()
    t.token = 'hash'
    t.text = ''
    #
    if not blob[i] == '#':
        raise Exception("bug!")
    i += 1
    #
    while True:
        [i,cc] = CSSllidentescapereadchar(blob,i,False)
        if cc == None:
            break
        t.text += cc
        first = False
    #
    return [i,t]

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
        if blob[i:i+4] == "<!--":
            i += 4
            t = CSSllToken()
            t.token = 'cdo'
            yield t
            continue
        if blob[i:i+3] == "-->":
            i += 3
            t = CSSllToken()
            t.token = 'cdc'
            yield t
            continue
        #
        if blob[i:i+4] == "url(":
            i += 4
            i = CSSskipwhitespace(blob,i)
            #
            t = CSSllToken()
            t.token = 'url'
            t.text = ''
            #
            while i < len(blob):
                begin = i
                i = CSSskipwhitespace(blob,i)
                if blob[i] == ')':
                    i += 1
                    break
                #
                if begin < i:
                    t.text += blob[begin:i]
                # CSS 2.x allows quotation marks in url() i.e. url("http://example.com");
                # CSS 3.x considers it a syntax error to have " ' ( ) \ whitespace or newline in the string.
                # What we'll do is just ignore " ' ( ), handle escapes anyway, and ignore newlines
                if blob[i] == '\"' or blob[i] == '\'' or blob[i] == '(' or blob[i] == ')' or blob[i] == '\n' or blob[i] == '\r' or blob[i] == '\t' or blob[i] == '\f':
                    i += 1
                    continue
                elif blob[i] == '\\':
                    [i,v] = CSSllescapereadchar(blob,i+1)
                    t.text += v
                else:
                    t.text += blob[i]
                    i += 1
            #
            yield t
            continue
        #
        r = CSSllIsIdentifier(blob,i)
        if r:
            [i,t] = CSSllParseIdentifier(r,blob,i)
            yield t
            continue
        #
        r = CSSllIsNumber(blob,i)
        if r:
            begin = i
            end = r.span()[1] + i
            i = end
            #
            t = CSSllToken()
            t.token = 'number'
            t.text = blob[begin:end]
            #
            if re.search(r'[\.eE]',t.text):
                t.value = float(t.text)
            else:
                t.value = int(t.text)
            #
            yield t
            continue
        #
        r = CSSllIsHash(blob,i)
        if r:
            [i,t] = CSSllParseHash(r,blob,i)
            yield t
            continue
        #
        if blob[i] == '\"' or blob[i] == '\'':
            match = blob[i]
            i += 1
            #
            t = CSSllToken()
            t.token = 'string'
            t.text = ''
            #
            while i < len(blob):
                if blob[i] == match:
                    i += 1
                    break
                #
                if blob[i] == '\\':
                    [i,v] = CSSllescapereadchar(blob,i+1)
                    t.text += v
                else:
                    t.text += blob[i]
                    i += 1
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

