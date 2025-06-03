#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

inFile = sys.argv[1]
lines = list(tabstospacesgen(rawtexttoutf8gen(rawtextsplitlinesgen(rawtextloadfile(inFile))),4))

class MarkdownElement:
    sub = None
    url = None
    key = None
    text = None
    link = None
    level = None
    title = None
    syntax = None
    reflabel = None
    elemType = None
    def __init__(self):
        self.sub = [ ] # MarkdownElement or instance of str
    def __str__(self):
        r = "[MarkdownElement"
        if not self.key == None:
            r += " key="+str(self.key)
        if not self.url == None:
            r += " url="+str(self.url)
        if not self.link == None:
            r += " link="+str(self.link)
        if not self.text == None:
            r += " text="+str(self.text)
        if not self.level == None:
            r += " level="+str(self.level)
        if not self.title == None:
            r += " title="+str(self.title)
        if not self.syntax == None:
            r += " syntax="+str(self.syntax)
        if not self.reflabel == None:
            r += " reflabel="+str(self.reflabel)
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

def skipwhitespace(line,end):
    while end < len(line) and line[end] == ' ':
        end += 1
    return end

def markdownsubst(line,mod={}):
    r = [ ]
    i = 0
    #
    accum = ''
    while i < len(line):
        beg = i
        end = len(line)
        j = re.search(r'([\_\*]{1,3}|\\|`{1,2}|\<|\[\!\[|\[|\!\[|(ftp|http|https)\:\/\/|mailto:[a-zA-Z0-9%\:]+\@[a-zA-Z0-9])',line[beg:end])
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
            elif what == '<': # URL
                end = span[0]
                accum += line[beg:end]
                end = span[0]+len(what)
                ei = findunescaped(line,'>',end)
                if ei < 0:
                    raise Exception("failed to find end")
                url = line[end:ei]
                end = ei+1
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                ce = MarkdownElement()
                ce.elemType = "link"
                ce.url = url
                r.append(ce)
            elif what == 'ftp://' or what == 'http://' or what == 'https://' or what[0:7] == 'mailto:': # auto URL conversion, except the trailing period is not counted.
                # make sure it's http://... and not zjklywqluiryuoiqwyrighttp://...
                end = span[0]
                if end == 0 or (end > 0 and line[end-1] == ' '):
                    accum += line[beg:end]
                    #
                    if len(accum) > 0:
                        r.append(accum)
                        accum = ''
                    #
                    beg = end
                    spn = re.search(r'[ \"\(\)\[\]\{\}]',line[beg:])
                    if spn:
                        end = spn.span()[0]+beg
                    else:
                        end = len(line)
                    # trailing periods don't count
                    if end > 0 and line[end-1] == '.':
                        end -= 1
                    #
                    url = line[beg:end]
                    #
                    ce = MarkdownElement()
                    ce.elemType = "link"
                    ce.url = url
                    r.append(ce)
                else:
                    end += len(what)
                    accum += line[beg:end]
            elif what == '`': # code
                if "ignore code" in mod:
                    end = span[0]+len(what)
                    accum += line[beg:end]
                else:
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
                        end = ei+1
                    #
                    if len(accum) > 0:
                        r.append(accum)
                        accum = ''
                    #
                    ce = MarkdownElement()
                    ce.elemType = "code"
                    ce.sub = markdownsubst(code,mod)
                    r.append(ce)
            elif what == '``': # escape code
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
                    end = ei+1
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                smod = mod.copy()
                smod['ignore code'] = True
                for s in markdownsubst(code,smod): # no need for whole sub element, make it inline to the subs
                    r.append(s)
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
                ce.sub = markdownsubst(code,mod)
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
                ce.sub = markdownsubst(code,mod)
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
                ce.sub = markdownsubst(code,mod)
                r.append(ce)
            elif what == '[' or what == '![' or what == '[![':
                end = span[0]
                accum += line[beg:end]
                end += len(what)
                #
                ei = findunescaped(line,']',end)
                if ei < 0:
                    raise Exception("failed to find end")
                reflinktarget = None
                reflabel = None
                title = None
                text = line[end:ei]
                link = None
                end = ei+1
                url = None
                #
                if len(accum) > 0:
                    r.append(accum)
                    accum = ''
                #
                if end < len(line) and line[end] == ':':
                    reflabel = text
                    text = None
                    end += 1
                    end = skipwhitespace(line,end)
                    #
                    if end < len(line) and line[end] == '<':
                        end += 1
                        ei = findunescaped(line,'>',end)
                        if ei < 0:
                            raise Exception("failed to find end")
                        url = line[end:ei]
                        end = ei+1
                    else:
                        ei = findunescaped(line,' ',end)
                        if ei < 0:
                            ei = len(line)
                        url = line[end:ei]
                        end = ei
                    reflinktarget = True
                    #
                    end = skipwhitespace(line,end)
                    #
                    if end < len(line) and (line[end] == '\'' or line[end] == '\"' or line[end] == '('):
                        if line[end] == '(':
                            match = ')'
                        else:
                            match = line[end]
                        end += 1
                        #
                        ei = findunescaped(line,match,end)
                        if ei < 0:
                            raise Exception("failed to find end")
                        text = line[end:ei]
                        end = ei+1
                else:
                    end = skipwhitespace(line,end)
                    #
                    if end < len(line) and line[end] == '[':
                        end += 1
                        ei = findunescaped(line,']',end)
                        if ei < 0:
                            raise Exception("failed to find end")
                        reflabel = line[end:ei]
                        end = ei+1
                    elif end < len(line) and line[end] == '(':
                        end += 1
                        ei = findunescaped(line,')',end)
                        if ei < 0:
                            raise Exception("failed to find end")
                        url = line[end:ei]
                        end = ei+1
                    #
                    if not url == None:
                        ei = url.find(' ')
                        if ei >= 0:
                            x = url[ei:].strip()
                            if x[0] == '\"' and x[-1] == '\"':
                                title = x[1:len(x)-1]
                            url = url[0:ei]
                    #
                #
                ce = MarkdownElement()
                #
                if what == '![' or what == '[![':
                    ce.elemType = "imagelink"
                elif reflinktarget == True:
                    ce.elemType = "reflinktarget"
                elif not reflabel == None:
                    ce.elemType = "reflink"
                else:
                    ce.elemType = "link"
                #
                if what == '[![':
                    end = skipwhitespace(line,end)
                    if end < len(line) and line[end] == ']':
                        end += 1
                    end = skipwhitespace(line,end)
                    if end < len(line) and line[end] == '(':
                        end += 1
                    ei = findunescaped(line,')',end)
                    if ei < 0:
                        raise Exception("failed to find end")
                    link = line[end:ei]
                    end = ei+1
                #
                ce.reflabel = reflabel
                ce.title = title
                ce.text = text
                ce.link = link
                ce.url = url
                r.append(ce)
                #
                end = skipwhitespace(line,end)
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

        # block quote
        if len(cline) > 1 and cline[0:2] == '> ':
            copylines = [ cline[2:] ]
            while i < len(lines):
                cline = lines[i]
                if len(cline) > 1 and cline[0:2] == '> ':
                    copylines.append(cline[2:])
                    i += 1
                elif cline == '>' or cline[0:2] == '>>':
                    copylines.append(cline[1:])
                    i += 1
                else:
                    break
            #
            ce = parsemarkdown(copylines)
            ce.elemType = "blockquote"
            mdRoot.sub.append(ce)
            #
            continue

        # unordered list
        # WARNING: Some Markdown interpreters consider anything part of the list if it is indented the same with spaces.
        #          For example:
        #
        #          - list item
        #
        #            something
        #
        #          - list item 2
        #
        #          We don't do that, we require the 4 spaces or tab that the Markdown Guide says it needs to be:
        #
        #          - list item
        #
        #              something indented by 4 spaces or tab
        #
        #          - list item 2
        if len(cline) > 1 and (cline[0] == '-' or cline[0] == '+' or cline[0] == '*') and cline[1] == ' ':
            match = cline[0]
            #
            ce = MarkdownElement()
            ce.elemType = "ulist"
            #
            cline = cline[2:]
            ue = MarkdownElement()
            ue.elemType = 'item'
            ue.sub = markdownsubst(cline.strip())
            ce.sub.append(ue)
            #
            while i < len(lines):
                cline = lines[i]
                if len(cline) == 0 or cline == "\t":
                    i += 1
                elif len(cline) > 1 and cline[0] == match and cline[1] == ' ':
                    cline = cline[2:]
                    i += 1
                    #
                    ue = MarkdownElement()
                    ue.elemType = 'item'
                    ue.sub = markdownsubst(cline.strip())
                    ce.sub.append(ue)
                elif len(cline) > 0 and cline[0] == '\t':
                    copylines = [ cline[1:] ]
                    i += 1
                    while i < len(lines):
                        cline = lines[i]
                        if len(cline) > 1 and cline[0] == '\t':
                            cline = cline[1:]
                            i += 1
                            copylines.append(cline)
                        elif len(cline) == 0 or cline == "\t":
                            i += 1
                        else:
                            break
                    #
                    for se in parsemarkdown(copylines).sub:
                        ce.sub.append(se)
                    #
                else:
                    break
            #
            mdRoot.sub.append(ce)
            continue

        # ordered list
        # the Markdown spec seems to imply the numbers don't matter, but to other interpreters it does.
        if len(cline) > 0:
            p = re.match(r'^(\d+)\. ',cline)
            if p:
                #
                ce = MarkdownElement()
                ce.elemType = "olist"
                #
                cline = cline[p.span()[1]:]
                number = int(p.groups()[0])
                ue = MarkdownElement()
                ue.elemType = 'item'
                ue.sub = markdownsubst(cline.strip())
                ue.key = number
                ce.sub.append(ue)
                #
                while i < len(lines):
                    cline = lines[i]
                    if len(cline) == 0 or cline == "\t":
                        i += 1
                    elif len(cline) > 0 and cline[0] == '\t':
                        copylines = [ cline[1:] ]
                        i += 1
                        while i < len(lines):
                            cline = lines[i]
                            if len(cline) > 1 and cline[0] == '\t':
                                cline = cline[1:]
                                i += 1
                                copylines.append(cline)
                            elif len(cline) == 0 or cline == "\t":
                                i += 1
                            else:
                                break
                        #
                        for se in parsemarkdown(copylines).sub:
                            ce.sub.append(se)
                    #
                    else:
                        p = re.match(r'^(\d+)\. ',cline)
                        if p:
                            cline = cline[p.span()[1]:]
                            number = int(p.groups()[0])
                            ue = MarkdownElement()
                            ue.elemType = 'item'
                            ue.sub = markdownsubst(cline.strip())
                            ue.key = number
                            ce.sub.append(ue)
                            i += 1
                        else:
                            break
                #
                mdRoot.sub.append(ce)
                continue

        # text in a paragraph can continue onto the next line
        while True:
            if cline[-2:] == "  ": # ends in at least two spaces or tabs
                break
            if nline == "":
                break
            if re.match(r'^[\-\*\#\~\`\>]',nline):
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
        print(indent+"-------STRING----------------------------------")
        print(md)
        print(indent+"-------END STRING------------------------------")
    else:
        print(indent+str(md))
        for sm in md.sub:
            dumpMD(sm,level+1)

# parse
mdRoot = parsemarkdown(lines)

# dump
dumpMD(mdRoot)

