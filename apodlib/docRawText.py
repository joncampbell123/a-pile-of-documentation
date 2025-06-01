
import re

def rawtextsplitlines(blob):
    return re.split(b'\n\r|\r\n|\r|\n',blob)

def rawtextsplitlines16le(blob):
    return re.split(b'\n\0\r\0|\r\0\n\0|\r\0|\n\0',blob)

def rawtextsplitlines16be(blob):
    return re.split(b'\0\n\0\r|\0\r\0\n|\0\r|\0\n',blob)

def rawtextloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

