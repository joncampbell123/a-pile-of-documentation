
import re

def htmlidfilter(x):
    return re.sub('[^a-zA-Z0-9_\-\.]','_',x)

def htmlescape(x):
    r = ""
    for c in x:
        if c == '<':
            r += "&lt;"
        elif c == '>':
            r += "&gt;"
        elif c == '&':
            r += "&amp;"
        elif c == '"':
            r += "&quot;"
        elif c == "'":
            r += "&apos;"
        else:
            r += c
    return r

def unescapeurl(x):
    rx = x.encode(encoding='UTF-8')
    r = b""
    i = 0
    while i < len(rx):
        if rx[i] == ord('%'):
            dig = "0x"+rx[i+1:i+3].decode(encoding='UTF-8')
            r += bytes([int(dig,base=16)])
            i = i + 3
        else:
            r += bytes([rx[i]])
            i = i + 1
    return r.decode(encoding='UTF-8')

# ex: <a id="t:source:id:sourceid:part:partid">...<a href="#t:source:id:sourceid:part:partid">duh</a>
def mkhtmlid(idtype,sid,path=None):
    r = "t:"+idtype+":id:"+sid
    if not path == None:
        for pelo in path:
            if "level" in pelo and "name" in pelo:
                r += ":" + htmlidfilter(pelo["level"]) + ":" + htmlidfilter(pelo["name"])
            elif "group index" in pelo:
                r += ":gi:" + str(pelo["group index"])
    return r

