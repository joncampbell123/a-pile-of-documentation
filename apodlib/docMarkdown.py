
import os
import re
import sys

from apodlib.docRawText import *

class MarkdownElement:
    sub = None
    url = None
    key = None
    text = None
    link = None
    align = None
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
        if not self.align == None:
            r += " align="+str(self.align)
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
    if end >= len(line):
        return end
    if not line[end] == ' ':
        return end
    #
    ei = re.search(r' +',line[end:])
    if ei:
        return end+ei.span()[1]
    else:
        return len(line)

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
                    if ei < 0: # not code
                        beg = end - len(what)
                        end = len(line)
                        accum += line[beg:end]
                    else:
                        code = line[end:ei]
                        end = ei+1
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

def splittablecols(line):
    line = line.strip()
    r = [ ]
    i = 0
    #
    if len(line) > 0 and line[0] == '|':
        line = line[1:]
    #
    if len(line) > 1 and line[-1] == '|' and not line[-2] == '\\|':
        line = line[0:len(line)-1]
    #
    while i < len(line):
        j = findunescaped(line,'|',i)
        if j < 0:
            j = len(line)
        #
        r.append(line[i:j])
        i = j+1
    #
    return r

def looksliketableseparators(cols):
    for col in cols:
        if not re.match(r'^[ \-\:]*-{3,}[ \-\:]*$',col):
            return False
    #
    return True

def parsemarkdown(lines):
    mdRoot = MarkdownElement()
    i = 0
    while i < len(lines):
        cline = lines[i]
        stcline = cline.lstrip()
        i += 1
        #
        if i < len(lines):
            nline = lines[i]
        else:
            nline = ''
        stnline = nline.lstrip()

        # ignore blank lines
        if stcline == "":
            continue

        # code block
        if cline[0:4] == "    ":
            spc = 4
            ce = MarkdownElement()
            ce.elemType = "codeblock"
            code = cline[spc:]
            while i < len(lines):
                cline = lines[i]
                if cline == "":
                    code += "\n"
                    i += 1
                elif cline[0:spc] == (" "*spc):
                    code += "\n" + cline[spc:]
                    i += 1
                else:
                    break
            # remove empty trailing lines
            ei = len(code) - 1
            while ei > 0 and code[ei-1] == '\n':
                ei -= 1
            code = code[0:ei]
            #
            ce.sub.append(code)
            mdRoot.sub.append(ce)
            continue

        # heading level 2
        #----------------
        if len(stcline) > 0 and re.match(r'^[^\-\*\#\~\`\|]',stcline) and re.match(r'^-+$',stnline):
            i += 1
            ce = MarkdownElement()
            ce.elemType = "heading"
            ce.level = 2
            ce.sub = markdownsubst(stcline)
            mdRoot.sub.append(ce)
            continue

        # heading level 1
        #================
        if len(stcline) > 0 and re.match(r'^[^\-\*\#\~\`\|]',stcline) and re.match(r'^=+$',stnline):
            i += 1
            ce = MarkdownElement()
            ce.elemType = "heading"
            ce.level = 1
            ce.sub = markdownsubst(stcline)
            mdRoot.sub.append(ce)
            continue

        # horizontal rule
        if re.match(r'^[\*\-\_]{3,}$',stcline):
            ce = MarkdownElement()
            ce.elemType = "hr"
            mdRoot.sub.append(ce)
            continue

        # heading
        x = re.match(r'^(#+)',stcline)
        if x:
            span = x.span()
            level = spanlen(span)
            ce = MarkdownElement()
            ce.elemType = "heading"
            ce.level = level
            ce.sub = markdownsubst(stcline[span[1]:].strip())
            mdRoot.sub.append(ce)
            continue

        # fenced code block (with optional language for syntax highlighting)
        x = re.match(r'^([\`\~]{3})([a-zA-Z0-9]*)',stcline)
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
                stcline = cline.lstrip()
                i += 1
                #
                if stcline[0:len(delim)] == delim:
                    break
                if not code == "":
                    code += "\n"
                code += cline
            #
            if not lang == None:
                ce.syntax = lang
            #
            ce.sub.append(code)
            mdRoot.sub.append(ce)
            continue

        # block quote
        if len(stcline) > 1 and stcline[0:2] == '> ':
            copylines = [ stcline[2:] ]
            while i < len(lines):
                stcline = lines[i].lstrip()
                if len(stcline) > 0 and stcline[0] == '>':
                    copylines.append(stcline[1:].lstrip())
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
        if len(stcline) > 1 and (stcline[0] == '-' or stcline[0] == '+' or stcline[0] == '*') and stcline[1] == ' ':
            this_spc = skipwhitespace(cline,0)
            match = stcline[0]
            #
            ce = MarkdownElement()
            ce.elemType = "ulist"
            #
            ue = MarkdownElement()
            ue.elemType = 'item'
            ue.sub = markdownsubst(stcline[2:].strip())
            ce.sub.append(ue)
            #
            while i < len(lines):
                cline = lines[i]
                spc = skipwhitespace(cline,0)
                stcline = cline[spc:]
                if len(stcline) == 0:
                    i += 1
                else:
                    if spc < this_spc:
                        break
                    elif spc >= (this_spc+2):
                        suspc = spc
                        #
                        copylines = [ cline[suspc:] ]
                        i += 1
                        while i < len(lines):
                            cline = lines[i]
                            spc = skipwhitespace(cline,0)
                            stcline = cline[spc:]
                            #
                            if len(stcline) > 0:
                                if spc < suspc:
                                    break
                                copylines.append(cline[suspc:])
                            else:
                                copylines.append(stcline)
                            i += 1
                        #
                        for se in parsemarkdown(copylines).sub:
                            ce.sub.append(se)
                        #
                    else:
                        if len(stcline) > 1 and stcline[0] == match and stcline[1] == ' ':
                            i += 1
                            #
                            ue = MarkdownElement()
                            ue.elemType = 'item'
                            ue.sub = markdownsubst(stcline[2:].strip())
                            ce.sub.append(ue)
                        else:
                            break
            #
            mdRoot.sub.append(ce)
            continue

        # ordered list
        # the Markdown spec seems to imply the numbers don't matter, but to other interpreters it does.
        if len(stcline) > 0:
            p = re.match(r'^ *(\d+)\. *',cline)
            if p:
                this_spc = skipwhitespace(cline,0)
                next_spc = p.span()[1]
                #
                ce = MarkdownElement()
                ce.elemType = "olist"
                #
                number = int(p.groups()[0])
                ue = MarkdownElement()
                ue.elemType = 'item'
                ue.sub = markdownsubst(cline[next_spc:].strip())
                ue.key = number
                ce.sub.append(ue)
                pkey = number
                #
                while i < len(lines):
                    cline = lines[i]
                    spc = skipwhitespace(cline,0)
                    stcline = cline[spc:]
                    if len(stcline) == 0:
                        i += 1
                    else:
                        if spc < this_spc:
                            break
                        elif spc >= next_spc:
                            suspc = spc
                            #
                            copylines = [ cline[suspc:] ]
                            i += 1
                            while i < len(lines):
                                cline = lines[i]
                                spc = skipwhitespace(cline,0)
                                stcline = cline[spc:]
                                #
                                if len(stcline) > 0:
                                    if spc < suspc:
                                        break
                                    copylines.append(cline[suspc:])
                                else:
                                    copylines.append(stcline)
                                i += 1
                            #
                            for se in parsemarkdown(copylines).sub:
                                ce.sub.append(se)
                            #
                        else:
                            p = re.match(r'^ *(\d+)\. *',cline)
                            if p:
                                number = int(p.groups()[0])
                                next_spc = p.span()[1]
                                ue = MarkdownElement()
                                ue.elemType = 'item'
                                ue.sub = markdownsubst(cline[next_spc:].strip())
                                # in this interpreter, giving the same number again means auto count
                                if not number == pkey:
                                    ue.key = number
                                #
                                ce.sub.append(ue)
                                pkey = number
                                i += 1
                            else:
                                break
                #
                mdRoot.sub.append(ce)
                continue

        # table?
        x = findunescaped(cline,'|',0)
        if x >= 0:
            headcols = splittablecols(cline)
            sepcols = splittablecols(nline)
            #
            if len(headcols) > 0 and len(sepcols) >= len(headcols):
                if looksliketableseparators(sepcols):
                    ncols = len(headcols)
                    tablealign = [ "left" ] * ncols
                    i += 1
                    #
                    for ci in range(0,min(ncols,min(len(sepcols),len(headcols)))):
                        col = sepcols[ci].strip()
                        cleft = False
                        cright = False
                        if col[0] == ':':
                            cleft = True
                        if col[-1] == ':':
                            cright = True
                        #
                        if cleft and cright:
                            tablealign[ci] = "center"
                        elif cleft:
                            tablealign[ci] = "left"
                        elif cright:
                            tablealign[ci] = "right"
                    #
                    te = MarkdownElement()
                    te.elemType = 'table'
                    #
                    he = MarkdownElement()
                    he.elemType = 'tableheadrow'
                    for ci in range(0,ncols):
                        col = headcols[ci].strip()
                        ce = MarkdownElement()
                        ce.elemType = 'tablecell'
                        ce.align = tablealign[ci]
                        ce.sub = markdownsubst(col)
                        he.sub.append(ce)
                    #
                    te.sub.append(he)
                    #
                    while i < len(lines):
                        stcline = lines[i].strip()
                        tabcols = splittablecols(stcline)
                        if len(tabcols) <= 1:
                            x = findunescaped(stcline,'|',0)
                            if x < 0:
                                break
                        #
                        he = MarkdownElement()
                        he.elemType = 'tablerow'
                        for ci in range(0,min(ncols,len(tabcols))):
                            col = tabcols[ci].strip()
                            ce = MarkdownElement()
                            ce.elemType = 'tablecell'
                            ce.align = tablealign[ci]
                            ce.sub = markdownsubst(col)
                            he.sub.append(ce)
                        #
                        te.sub.append(he)
                        i += 1
                    #
                    mdRoot.sub.append(te)
                    continue

        # text in a paragraph can continue onto the next line
        cline = cline.lstrip()
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

