
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

class htmlelem:
    tag = None # string
    attr = None # object (dict) key=string, value=string
    content = None # binary
    def __init__(self,tag,attr={ },content=None):
        self.content = self.encodecontent(content)
        self.attr = attr
        self.tag = tag
    def encodecontent(self,content):
        if isinstance(content,list):
            r = b""
            for cent in content:
                r += self.encodecontent(cent)
            return r
        else:
            if not content == None and isinstance(content,str):
                return htmlescape(content).encode('UTF-8')
            elif isinstance(content,htmlelem): # we allow tags within tags here
                return content.gettag()
            else:
                return content
    def opentag(self):
        return b"<"+self.tagcontent()+b">"
    def closetag(self):
        return b"</"+self.tag.encode('UTF-8')+b">"
    def octag(self):
        return b"<"+self.tagcontent()+b" />"
    def tagcontent(self):
        r = self.tag.encode('UTF-8')
        if not self.attr == None and type(self.attr) == dict and len(self.attr) > 0:
            for key in self.attr:
                val = self.attr[key]
                r += b" "+key.encode('UTF-8')
                if not val == None:
                    r += b"=\""+htmlescape(val).encode('UTF-8')+b"\""
        return r
    def gettag(self):
        # NTS: Mozilla Firefox seems to have a problem with <a id="blah" />, it seems to format
        #      the DOM as if everything following it is contained within the anchor element.
        #      The fact that the tag is self-closing seems lost on Mozilla.
        if not self.content == None or self.tag.lower() == "a":
            r = self.opentag()
            if not self.content == None:
                r += self.content
            r += self.closetag()
            return r
        else:
            return self.octag()

class htmlwriter:
    content = None
    stack = None
    def __init__(self):
        self.content = None
        self.stack = [ ]
    def out(self,x):
        if self.content == None:
            self.content = b""
        self.content += x
    def topelemopen(self):
        if len(self.stack) > 0 and self.stack[-1].content == None:
            self.stack[-1].content = b""
            self.out(self.stack[-1].opentag())
    def topelemclose(self):
        if len(self.stack) > 0:
            if self.stack[-1].content == None:
                self.out(self.stack[-1].octag())
            else:
                self.out(self.stack[-1].closetag())
    def write(self,whtmlelem):
        self.topelemopen()
        self.out(whtmlelem.gettag())
    def get(self):
        if len(self.stack) > 0:
            raise Exception("Attempt to render HTML without closing all tags with end()")
        if not self.content == None:
            r = self.content
        else:
            r = b""
        self.content = None
        return r
    def begin(self,htmlelem):
        self.topelemopen()
        self.stack.append(htmlelem)
    def end(self):
        if len(self.stack) == 0:
            raise Exception("HTML end with nothing left")
        self.topelemclose()
        self.stack.pop()

