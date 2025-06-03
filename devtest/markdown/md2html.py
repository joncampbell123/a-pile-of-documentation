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
        sys.stdout.write(html_escape(md))
    else:
        tag = None
        #
        if md.elemType == None:
            True
        elif md.elemType == 'paragraph':
            tag = 'p'
        elif md.elemType == 'heading':
            tag = 'h'+str(md.level)
        elif md.elemType == 'hr':
            tag = 'hr'
        elif md.elemType == 'italic':
            tag = 'em'
        elif md.elemType == 'bold':
            tag = 'b'
        elif md.elemType == 'bold+italic':
            tag = 'b+i'
        elif md.elemType == 'code':
            tag = 'code'
        elif md.elemType == 'codeblock':
            tag = 'codeblock'
        else:
            True
            #print("\n? "+str(md.elemType))
        #
        if tag == None:
            for ent in md.sub:
                emit_mde(ent)
        elif len(md.sub) > 0:
            if tag == 'b+i':
                sys.stdout.write("<em><b>")
            else:
                sys.stdout.write("<"+tag+">")
            #
            for ent in md.sub:
                emit_mde(ent)
            #
            if tag == 'b+i':
                sys.stdout.write("</b></em>")
            else:
                sys.stdout.write("</"+tag+">")
        else:
            if tag == 'b+i':
                True
            else:
                sys.stdout.write("<"+tag+"/>")

sys.stdout.write("<!DOCTYPE html>")
sys.stdout.write("<html>")
sys.stdout.write("<head>")
sys.stdout.write("<meta charset=\"utf-8\">\n")
sys.stdout.write("<style>\n")
sys.stdout.write("codeblock { white-space: pre-wrap; text-wrap-mode: nowrap; font-family: monospace, monospace; padding: 0.7em; display: block; }\n");
sys.stdout.write("</style>\n")
sys.stdout.write("</head>")
sys.stdout.write("<body>")
emit_mde(mdRoot)
sys.stdout.write("</body>")
sys.stdout.write("</html>")

