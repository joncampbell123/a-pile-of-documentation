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

def emit_mde(md,mod={}):
    if isinstance(md,str):
        sys.stdout.write(html_escape(md))
    else:
        tag = None
        attr = ''
        smod = mod.copy()
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
        elif md.elemType == 'table':
            tag = 'table'
        elif md.elemType == 'tableheadrow':
            smod['tablerow'] = 'head'
            tag = 'tr'
        elif md.elemType == 'tablerow':
            smod['tablerow'] = 'body'
            tag = 'tr'
        elif md.elemType == 'blockquote':
            tag = 'blockquote'
        elif md.elemType == 'tablecell':
            if smod['tablerow'] == "head":
                tag = "th"
            else:
                tag = "td"
            #
            if md.align == 'left':
                attr += ' class="leftalign"'
            elif md.align == 'center':
                attr += ' class="centeralign"'
            elif md.align == 'right':
                attr += ' class="rightalign"'
        elif md.elemType == 'link':
            sys.stdout.write("<a")
            #
            if not md.url == None:
                if re.match(r'\"',md.url):
                    raise Exception("Quotes in markdown")
                sys.stdout.write(" href=\""+md.url+"\"")
            if not md.title == None:
                if re.match(r'\"',md.title):
                    raise Exception("Quotes in markdown")
                sys.stdout.write(" title=\""+md.title+"\"")
            #
            sys.stdout.write(">")
            #
            if not md.text == None:
                sys.stdout.write(html_escape(md.text))
            #
            sys.stdout.write("</a>")
        else:
            #print("\n? "+str(md.elemType))
            True
        #
        if tag == None:
            for ent in md.sub:
                emit_mde(ent,smod)
        elif len(md.sub) > 0:
            if tag == 'b+i':
                sys.stdout.write("<em><b>")
            else:
                sys.stdout.write("<"+tag+attr+">")
            #
            for ent in md.sub:
                emit_mde(ent,smod)
            #
            if tag == 'b+i':
                sys.stdout.write("</b></em>")
            else:
                sys.stdout.write("</"+tag+">")
        else:
            if tag == 'b+i':
                True
            else:
                sys.stdout.write("<"+tag+attr+"/>")

sys.stdout.write("<!DOCTYPE html>")
sys.stdout.write("<html>")
sys.stdout.write("<head>")
sys.stdout.write("<meta charset=\"utf-8\">\n")
sys.stdout.write("<style>\n")
sys.stdout.write("codeblock { white-space: pre-wrap; text-wrap-mode: nowrap; font-family: monospace, monospace; padding: 0.7em; display: block; }\n");
sys.stdout.write("blockquote { padding: 0.35em; padding-left: 0.75em; border-left: 1.0em solid #7f7f7f; display: block; background: #cfcfcf; }\n");
sys.stdout.write("table { border: 1px solid #9f9f9f; padding: 0.25em; border-collapse: collapse; margin-top: 0.75em; margin-bottom: 0.75em; }\n");
sys.stdout.write("th { border: 1px solid #9f9f9f; padding: 0.25em; }\n");
sys.stdout.write("td { border: 1px solid #9f9f9f; padding: 0.25em; }\n");
sys.stdout.write(".leftalign { text-align: left; }\n");
sys.stdout.write(".centeralign { text-align: center; }\n");
sys.stdout.write(".rightalign { text-align: right; }\n");
sys.stdout.write("</style>\n")
sys.stdout.write("</head>")
sys.stdout.write("<body>")
emit_mde(mdRoot)
sys.stdout.write("</body>")
sys.stdout.write("</html>")

