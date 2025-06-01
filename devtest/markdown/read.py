#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

inFile = sys.argv[1]
lines = list(spacestotabsgen(rawtexttoutf8gen(rawtextsplitlinesgen(rawtextloadfile(inFile))),4))

class MarkdownElement:
    sub = None
    level = None
    elemType = None
    def __init__(self):
        self.sub = [ ] # MarkdownElement or instance of str

def spanlen(span):
    if span:
        return span[1] - span[0]
    return 0

mdRoot = MarkdownElement()
i = 0
while i < len(lines):
    cline = lines[i]
    i += 1
    if i < len(lines):
        nline = lines[i]
    else:
        nline = ''

    # ignore blank lines
    if cline == "":
        continue

    # heading level 2
    #----------------
    if len(cline) > 0 and re.match(r'^[^\-\*\#]',cline) and re.match(r'^-+$',nline):
        i += 1
        ce = MarkdownElement()
        ce.elemType = "heading"
        ce.level = 2
        ce.sub.append(cline)
        mdRoot.sub.append(ce)
        continue

    # heading level 1
    #================
    if len(cline) > 0 and re.match(r'^[^\-\*\#]',cline) and re.match(r'^=+$',nline):
        i += 1
        ce = MarkdownElement()
        ce.elemType = "heading"
        ce.level = 1
        ce.sub.append(cline)
        mdRoot.sub.append(ce)
        continue

    # horizontal rule
    if re.match(r'^[\*\-\_]{3,}$',cline):
        ce = MarkdownElement()
        ce.elemType = "hr"
        mdRoot.sub.append(ce)
        continue

    # heading
    x = re.match(r'^(#+)',cline)
    if x:
        span = x.span()
        level = spanlen(span)
        ce = MarkdownElement()
        ce.elemType = "heading"
        ce.level = level
        ce.sub.append(cline[span[1]:].strip())
        mdRoot.sub.append(ce)
        continue

    # code block (remember, this is why the regex above to convert four spaces into tabs)
    if cline[0] == "\t":
        ce = MarkdownElement()
        ce.elemType = "codeblock"
        code = re.sub(r'\t','    ',cline[1:]) # convert back to spaces after stripping tab
        while i < len(lines):
            cline = lines[i]
            if cline == "":
                code += "\n"
                i += 1
            elif cline[0] == "\t":
                code += "\n" + re.sub(r'\t','    ',cline[1:])
                i += 1
            else:
                break
        ce.sub.append(code)
        mdRoot.sub.append(ce)
        continue

    # text in a paragraph can continue onto the next line
    while True:
        if cline[-2:] == "  ": # ends in at least two spaces or tabs
            break
        if nline == "":
            break
        if re.match(r'^[`#]',nline):
            break
        cline += " " + nline.strip()
        #
        i += 1
        if i < len(lines):
            nline = lines[i]
        else:
            nline = ''

    # anything else is just text
    mdRoot.sub.append(cline)

