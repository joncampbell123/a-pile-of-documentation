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
    syntax = None
    elemType = None
    def __init__(self):
        self.sub = [ ] # MarkdownElement or instance of str
    def __str__(self):
        r = "[MarkdownElement"
        if not self.level == None:
            r += " level="+str(self.level)
        if not self.syntax == None:
            r += " syntax="+str(self.syntax)
        if not self.elemType == None:
            r += " elemType="+str(self.elemType)
        r += "]"
        return r

def spanlen(span):
    if span:
        return span[1] - span[0]
    return 0

def findunescaped(line,what,start):
    ei = -1
    i = line.find(what,start)
    while True:
        if i > 0 and line[i-1] == '\\':
            start = i+1
            i = line.find(what,start)
        else:
            ei = i
            break
    return ei

def markdownsubst(line):
    r = [ ]
    i = 0
    #
    accum = ''
    while i < len(line):
        beg = i
        end = len(line)
        j = re.search(r'([\[\_\*]{1,3}|[\\\`])',line[beg:end])
        if j:
            span = j.span()
            span = [span[0]+beg,span[1]+beg]
            what = line[span[0]:span[1]]
            #
            if what[0] == '\\':
                end = span[0]
                accum += line[beg:end]
                what = line[span[0]:span[0]+2]
                end = span[0]+2
                accum += what[1]
            elif what == '`': # code
                end = span[0]
                accum += line[beg:end]
                end += 1
                #
                ei = findunescaped(line,what,end)
                if ei < 0:
                    code = line[end:]
                    end = len(line)
                else:
                    code = line[end:ei]
                    end = ei+1
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                ce = MarkdownElement()
                ce.elemType = "code"
                ce.sub = markdownsubst(code)
                r.append(ce)
            elif what == '*' or what == '_': # italic
                end = span[0]
                accum += line[beg:end]
                end += len(what)
                #
                ei = findunescaped(line,what,end)
                if ei < 0:
                    code = line[end:]
                    end = len(line)
                else:
                    code = line[end:ei]
                    end = ei+len(what)
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                ce = MarkdownElement()
                ce.elemType = "italic"
                ce.sub = markdownsubst(code)
                r.append(ce)
            elif what == '**' or what == '__': # bold
                end = span[0]
                accum += line[beg:end]
                end += len(what)
                #
                ei = findunescaped(line,what,end)
                if ei < 0:
                    code = line[end:]
                    end = len(line)
                else:
                    code = line[end:ei]
                    end = ei+len(what)
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                ce = MarkdownElement()
                ce.elemType = "bold"
                ce.sub = markdownsubst(code)
                r.append(ce)
            elif re.match(r'^[\_\*]{3}$',what): # bold+italic
                end = span[0]
                accum += line[beg:end]
                end += len(what)
                #
                ei = findunescaped(line,what,end)
                if ei < 0:
                    code = line[end:]
                    end = len(line)
                else:
                    code = line[end:ei]
                    end = ei+len(what)
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                ce = MarkdownElement()
                ce.elemType = "bold+italic"
                ce.sub = markdownsubst(code)
                r.append(ce)
            else:
                end = span[0]+1
                accum += line[beg:end]
        else:
            accum += line[beg:end]

        i = end
    #
    if len(accum) > 0:
        r.append(accum)
        accum = ''
    return r

def parsemarkdown(lines):
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
        if len(cline) > 0 and re.match(r'^[^\-\*\#\~\`]',cline) and re.match(r'^-+$',nline):
            i += 1
            ce = MarkdownElement()
            ce.elemType = "heading"
            ce.level = 2
            ce.sub = markdownsubst(cline)
            mdRoot.sub.append(ce)
            continue

        # heading level 1
        #================
        if len(cline) > 0 and re.match(r'^[^\-\*\#\~\`]',cline) and re.match(r'^=+$',nline):
            i += 1
            ce = MarkdownElement()
            ce.elemType = "heading"
            ce.level = 1
            ce.sub = markdownsubst(cline)
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
            ce.sub = markdownsubst(cline[span[1]:].strip())
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

        # fenced code block (with optional language for syntax highlighting)
        x = re.match(r'^([\`\~]{3})([a-zA-Z0-9]*)',cline)
        if x:
            ce = MarkdownElement()
            ce.elemType = "codeblock"
            #
            g = x.groups() # [```|~~~] and possible the lang
            delim = g[0]
            lang = None
            if len(g) > 1:
                lang = g[1]
            #
            code = ""
            #
            while i < len(lines):
                cline = lines[i]
                i += 1
                #
                if cline[0:len(delim)] == delim:
                    break
                if not code == "":
                    code += "\n"
                code += re.sub(r'\t','    ',cline)
            #
            if not lang == None:
                ce.syntax = lang
            #
            ce.sub.append(code)
            mdRoot.sub.append(ce)
            continue

        # text in a paragraph can continue onto the next line
        while True:
            if cline[-2:] == "  ": # ends in at least two spaces or tabs
                break
            if nline == "":
                break
            if re.match(r'^[\-\*\#\~\`]',nline):
                break
            cline += " " + nline.strip()
            #
            i += 1
            if i < len(lines):
                nline = lines[i]
            else:
                nline = ''

        # anything else is just text in a paragraph
        ce = MarkdownElement()
        ce.elemType = "paragraph"
        ce.sub = markdownsubst(cline)
        mdRoot.sub.append(ce)
    #
    return mdRoot

def dumpMD(md,level=0):
    indent=' '*level*2
    if isinstance(md,str):
        print("-------STRING----------------------------------")
        print(md)
        print("-------END STRING------------------------------")
    else:
        print(indent+str(md))
        for sm in md.sub:
            dumpMD(sm,level+1)

# parse
mdRoot = parsemarkdown(lines)

# dump
dumpMD(mdRoot)

