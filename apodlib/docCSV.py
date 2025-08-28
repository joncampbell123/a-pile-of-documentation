
import os
import re
import sys

def rawcsvloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

class CSVReaderState:
    encoding = 'UTF-8'

def CSVllParse(blob,state=CSVReaderState()):
    txt = blob.decode(state.encoding)
    #
    i = 0
    while i < len(txt):
        p = re.match(r'[ \t]*\"',txt[i:])
        if p:
            field = ""
            i = p.span()[1] + i
            while i < len(txt):
                p = re.search(r'(\"\"|\"|\r\n|\n)',txt[i:])
                if p:
                    what = p.groups()[0]
                    at = p.span()[0] + i
                    en = p.span()[1] + i
                    # field
                    if i < at:
                        field += txt[i:at]
                        i = at
                    #
                    begin = i = en
                    #
                    if what == '\"':
                        while i < len(txt) and (txt[i] == ' ' or txt[i] == '\t'):
                            i += 1
                        if i < len(txt) and txt[i] == ',':
                            i += 1
                        break
                    elif what == '\"\"':
                        field += '\"'
                    elif what == '\n' or what == '\r\n':
                        field += '\n'
                else:
                    field += txt[i:]
                    i = len(txt)
            #
            yield field
        else:
            p = re.search(r'(,|\r\n|\n)',txt[i:])
            if p:
                what = p.groups()[0]
                at = p.span()[0] + i
                en = p.span()[1] + i
                # field
                if i < at or what == ',':
                    yield txt[i:at]
                    i = at
                #
                begin = i = en
                #
                if what == "\n" or what == "\r\n":
                    yield "\n"
            else:
                yield txt[i:]
                i = len(txt)
                break

