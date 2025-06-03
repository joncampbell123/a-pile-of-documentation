#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *
from apodlib.docMarkdown import *

inFile = sys.argv[1]
lines = list(tabstospacesgen(rawtexttoutf8gen(rawtextsplitlinesgen(rawtextloadfile(inFile))),4))
mdRoot = parsemarkdown(lines)

def html_escape(md):
    i = 0
    r = ""
    while i < len(md):
        j = re.search(r'([\&\<\>])',md[i:])
        if j:
            what = j.groups()[0]
            iend = j.span()[0]+i
            mend = j.span()[1]+i
            r += md[i:iend]
            i = mend
            #
            if what == "&":
                r += "&amp;"
            elif what == "<":
                r += "&lt;"
            elif what == ">":
                r += "&gt;"
        else:
            r += md[i:]
            i = len(md)
    return r

def emit_mde(md):
    if isinstance(md,str):
        print(html_escape(md))
    else:
        tag = None
        #
        if md.elemType == 'paragraph':
            tag = 'p'
        elif md.elemType == 'heading':
            tag = 'h'+str(md.level)
        #
        if tag == None:
            for ent in md.sub:
                emit_mde(ent)
        elif len(md.sub) > 0:
            print("<"+tag+">")
            for ent in md.sub:
                emit_mde(ent)
            print("</"+tag+">")
        else:
            print("<"+tag+"/>")

print("<!DOCTYPE html>")
print("<html>")
print("<head>")
print("<meta charset=\"utf-8\">")
print("</head>")
print("<body>")
emit_mde(mdRoot)
print("</body>")
print("</html>")

