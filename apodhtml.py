
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

