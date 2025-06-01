
import re

def rawtextsplitlines(blob):
    return re.split(b'\n\r|\r\n|\r|\n',blob)

def rawtextloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

