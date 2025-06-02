
import re

def rawtextsplitlines(blob):
    return re.split(b'\n\r|\r\n|\r|\n',blob)

def rawtextsplitlines16le(blob):
    return re.split(b'\n\0\r\0|\r\0\n\0|\r\0|\n\0',blob)

def rawtextsplitlines16be(blob):
    return re.split(b'\0\n\0\r|\0\r\0\n|\0\r|\0\n',blob)

# with generators!

def rawtextsplitlinesgen(blob):
    for line in re.split(b'\n\r|\r\n|\r|\n',blob):
        yield line
    return None

def rawtexttoutf8gen(g):
    for line in g:
        yield line.decode('utf-8')
    return None

def spacestotabsgen(lit,tabs):
    rex = r' ' * tabs;
    for line in lit:
        yield re.sub(rex,'\t',line)

def tabstospacesgen(lit,tabs):
    for line in lit:
        yield re.sub('\t',' '*tabs,line)

# load file

def rawtextloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

