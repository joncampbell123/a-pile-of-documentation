
import os
import re
import sys

from apodlib.docHTMLCSS import *

class CSSmidState:
    blob = None
    bliter = None
    llstate = None
    lookahead = None
    comments = None
    prev = None # warning: prev token returned by get()
    last = None # warning: last token returned by get()
    def __init__(self):
        self.comments = [ ]
        self.lookahead = [ ]
        self.llstate = CSSllState()
    def start(self,blob):
        self.blob = blob
        self.bliter = iter(CSSllparse(self.blob,self.llstate))
    def peek(self,i=0):
        while len(self.lookahead) <= i:
            try:
                t = next(self.bliter)
                if t.token == 'comment':
                    self.comments.append(t)
                else:
                    self.lookahead.append(t)
            except StopIteration:
                self.lookahead.append(CSSllToken())
        #
        return self.lookahead[i]
    def get(self):
        self.prev = self.last
        self.last = r = self.peek()
        self.discard()
        return r
    def discard(self): # TODO: Add second parameter i if multiple token discard is ever needed
        self.peek() # fill lookahead
        #
        if len(self.lookahead) < 1:
            raise Exception("OOPS")
        #
        self.lookahead = self.lookahead[1:]
    def skipwhitespace(self):
        while self.peek().token == 'ws':
            self.discard()

inFile = sys.argv[1]
rawcss = rawcssloadfile(inFile)

state = CSSmidState()

class CSSAttributeSelector:
    value = None
    howMatch = None
    # None=[att]
    # 'exact'=[att=value]
    # 'any'=[att~=value]
    # 'begin-dash'=[att=|=value]
    # 'begins'=[att^=value]
    # 'ends'=[att$=value]
    # 'substr'=[att*=value]
    attribute = None
    def __str__(self):
        r = "[CSSAttributeSelector"
        if not self.attribute == None:
            r += " attribute="+str(self.attribute)
        if not self.howMatch == None:
            r += " howMatch="+str(self.howMatch)
        if not self.value == None:
            r += " value="+str(self.value)
        r += "]"
        return r

class CSSPseudoClassSelector:
    name = None # :class
    tokens = None # :class(...)
    def __str__(self):
        r = "[CSSPseudoClassSelector"
        if not self.name == None:
            r += " name="+str(self.name)
        if not self.tokens == None:
            r += " tokens=("
            c = 0
            for ent in self.tokens:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        r += "]"
        return r
    def __init__(self):
        self.tokens = [ ]

class CSSSimpleSelector:
    pseudoElementSelectors = None
    pseudoClassSelectors = None
    classSelectors = None
    attrSelectors = None
    typeSelector = None
    idSelectors = None
    def __init__(self):
        self.pseudoElementSelectors = [ ]
        self.pseudoClassSelectors = [ ]
        self.classSelectors = [ ]
        self.attrSelectors = [ ]
        self.idSelectors = [ ]
    def __bool__(self):
        if len(self.pseudoElementSelectors) > 0:
            return True
        if len(self.pseudoClassSelectors) > 0:
            return True
        if len(self.classSelectors) > 0:
            return True
        if not self.typeSelector == None:
            return True
        if len(self.attrSelectors) > 0:
            return True
        if len(self.idSelectors) > 0:
            return True
        return False
    def __str__(self):
        r = "[CSSSimpleSelector"
        if not self.typeSelector == None:
            r += " typeSelector="+str(self.typeSelector)
        if not self.idSelectors == None:
            r += " idSelector=("
            c = 0
            for ent in self.idSelectors:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        if not self.attrSelectors == None:
            r += " attrSelector=("
            c = 0
            for ent in self.attrSelectors:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        if not self.classSelectors == None:
            r += " classSelector=("
            c = 0
            for ent in self.classSelectors:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        if not self.pseudoClassSelectors == None:
            r += " pseudoClassSelector=("
            c = 0
            for ent in self.pseudoClassSelectors:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        if not self.pseudoElementSelectors == None:
            r += " pseudoElementSelector=("
            c = 0
            for ent in self.pseudoElementSelectors:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        r += "]"
        return r

def CSSParseSimpleSelector(state,ss): # CSSSimpleSelector
    state.skipwhitespace()
    t = state.peek()
    if t.token == 'ident' or (t.token == 'char' and t.text == '*'):
        ss.typeSelector = t.text
        state.discard()
    #
    while True:
        t = state.peek()
        if t.token == 'hash': # #id
            ss.idSelectors.append(t.text)
            state.discard()
        elif t.token == 'class': # .class
            ss.classSelectors.append(t.text)
            state.discard()
        elif t.token == 'char' and t.text == '[': # [attribute]
            attr = CSSAttributeSelector()
            state.discard()
            #
            t = state.peek()
            if t.token == 'ident':
                attr.attribute = t.text
                state.discard()
            else:
                raise Exception("CSS attribute selector parsing error "+str(t))
            #
            t = state.peek(0)
            t2 = state.peek(1)
            if not t:
                break
            if t.token == 'char' and t.text == '=':
                attr.howMatch = 'exact'
                state.discard()
            elif t.token == 'char' and t.text == '~' and t2.token == 'char' and t2.text == '=':
                attr.howMatch = 'any'
                state.discard()
                state.discard()
            elif t.token == 'char' and t.text == '|' and t2.token == 'char' and t2.text == '=':
                attr.howMatch = 'begin-dash'
                state.discard()
                state.discard()
            elif t.token == 'char' and t.text == '^' and t2.token == 'char' and t2.text == '=':
                attr.howMatch = 'begins'
                state.discard()
                state.discard()
            elif t.token == 'char' and t.text == '$' and t2.token == 'char' and t2.text == '=':
                attr.howMatch = 'ends'
                state.discard()
                state.discard()
            elif t.token == 'char' and t.text == '*' and t2.token == 'char' and t2.text == '=':
                attr.howMatch = 'substr'
                state.discard()
                state.discard()
            #
            if not attr.howMatch == None:
                attr.value = ''
                while True:
                    t = state.peek()
                    if not t:
                        break
                    if t.token == 'char' and t.text == ']':
                        break
                    attr.value += t.text
                    state.discard()
            #
            t = state.peek()
            if t.token == 'char' and t.text == ']':
                ss.attrSelectors.append(attr)
                state.discard()
                break
            else:
                raise Exception("CSS attribute selector expected closure "+str(t))
        else:
            break
    #
    while True:
        t = state.peek()
        if t.token == 'char' and t.text == ':':
            t = state.peek(1)
            if t.token == 'char' and t.text == ':':
                # ::pseudoelement
                t = state.peek(2)
                if t.token == 'ident':
                    ss.pseudoElementSelectors.append(t.text)
                    state.discard() # discard :
                    state.discard() # discard :
                    state.discard() # discard ident
                    continue
            else:
                # :pseudoclass
                if t.token == 'ident':
                    ent = CSSPseudoClassSelector()
                    ent.name = t.text
                    state.discard() # discard :
                    state.discard() # discard ident
                    ss.pseudoClassSelectors.append(ent)
                    continue
                # :pseudoclass(
                elif t.token == 'function':
                    ent = CSSPseudoClassSelector()
                    ent.name = t.text
                    state.discard() # discard :
                    state.discard() # discard function(
                    while True:
                        t = state.get()
                        if not t:
                            break
                        if t.token == 'char' and t.text == ')':
                            break
                        ent.tokens.append(t)
                    #
                    ss.pseudoClassSelectors.append(ent)
                    continue
        break
    #
    return ss

class CSSSelector:
    rules = None # CSSSimpleSelector or ' ' or '+' or '>'
    def __init__(self):
        self.rules = [ ]
    def __bool__(self):
        if len(self.rules) > 0:
            return True
        return False
    def __str__(self):
        r = "[CSSSelector"
        if not self.rules == None:
            r += " rules=("
            c = 0
            for ent in self.rules:
                if c > 0:
                    r += " "
                if isinstance(ent,str):
                    r += "\""+ent+"\""
                else:
                    r += str(ent)
                c += 1
            r += ")"
        r += "]"
        return r

class CSSAtRule:
    name = None
    blocks = None
    tokens = None
    def __init__(self):
        self.tokens = [ ]
        self.blocks = [ ]
    def __str__(self):
        r = "[CSSAtRule"
        if not self.name == None:
            r += " name="+str(self.name)
        if not self.blocks == None:
            r += " blocks=("
            c = 0
            for ent in self.blocks:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        if not self.tokens == None:
            r += " tokens=("
            c = 0
            for ent in self.tokens:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        r += "]"
        return r;

class CSSMatchRule:
    rules = None # CSSSelector
    def __init__(self):
        self.rules = [ ]
    def __str__(self):
        r = "[CSSMatchRule"
        if not self.rules == None:
            r += " rules=("
            c = 0
            for ent in self.rules:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"
        r += "]"
        return r

class CSSNameValue:
    name = None
    value = None
    def __str__(self):
        r = "[CSSNameValue"
        if not self.name == None:
            r += " name="+self.name
        if not self.value == None:
            if self.valueType == 'tokens':
                r += " tokens=("
                c = 0
                for t in self.value:
                    if c > 0:
                        r += " "
                    r += str(t)
                    c += 1
                r += ")"
        r += "]"
        return r

class CSSBlock:
    atrule = None # CSSAtRule
    rule = None # CSSMatchRule
    nvlist = None # CSSNameValue
    subblocklist = [ ] # CSSBlock
    def __init__(self):
        self.rule = CSSMatchRule()
        self.subblocklist = [ ]
        self.nvlist = { }
    def __str__(self):
        r = "[CSSBlock"
        if not self.rule == None:
            r += " rule="
            r += str(self.rule)
        if not self.atrule == None:
            r += " atrule="
            r += str(self.atrule)
        if not self.nvlist == None:
            r += " nv=("
            c = 0
            for i,(name,vallist) in enumerate(self.nvlist.items()):
                for val in vallist:
                    if c > 0:
                        r += " "
                    r += str(name)+":"+str(val)
                    c += 1
            r += ")"
        if not self.subblocklist == None:
            r += " subblocklist=("
            c = 0
            for ent in self.subblocklist:
                if c > 0:
                    r += " "
                r += str(ent)
                c += 1
            r += ")"

        r += "]"
        return r

def CSSLooksAheadSelectorsAndBlock(state):
    i = 0
    while True:
        t = state.peek(i)
        i += 1
        #
        if t.token == 'ident' or t.token == 'class' or t.token == 'hash' or t.token == 'ws':
            True
        elif t.token == 'char' and (t.text == '+' or t.text == '>' or t.text == '*' or t.text == '~'):
            True
        elif t.token == 'at-keyword':
            return True
        elif t.token == 'char' and t.text == '{':
            return True
        else:
            break
    #
    return False

def CSSBlockNVParse(state,css): # CSSBlock
    # already took { token
    while True:
        state.skipwhitespace()
        #
        if CSSLooksAheadSelectorsAndBlock(state):
            #
            # do NOT discard tokens, the block parser needs them
            #
            subcss = CSSOneBlock(state)
            if subcss == None:
                break
            css.subblocklist.append(subcss)
            continue
        #
        t = state.get()
        if not t:
            break
        if t.token == 'char' and t.text == '}':
            break
        # name
        nv = CSSNameValue()
        if t.token == 'ident':
            nv.name = t.text
        else:
            raise Exception("CSS parsing error expect name "+str(t))
        # value
        state.skipwhitespace()
        t = state.get()
        if not t:
            break
        if t.token == 'char' and t.text == ':':
            nv.valueType = 'tokens'
            nv.value = [ ]
            state.skipwhitespace()
            while True:
                t = state.peek()
                if t.token == 'char' and t.text == '}': # *sigh* minified CSS tends to omit ; if closing a block
                    break
                t = state.get()
                if t.token == 'char' and t.text == ';':
                    break
                if not t:
                    break
                nv.value.append(t)
        else:
            raise Exception("CSS parsing error expect colon+value")
        #
        if nv.name in css.nvlist:
            vl = css.nvlist[nv.name]
        else:
            vl = css.nvlist[nv.name] = [ ]
        #
        vl.append(nv)

def CSSSelectorParse(state,css):
    while True:
        sel = CSSSelector()
        while True:
            ss = CSSSimpleSelector()
            CSSParseSimpleSelector(state,ss) # reads and discards tokens
            if ss:
                sel.rules.append(ss)
            else:
                break
            #
            ws = False
            t = state.peek()
            if t.token == 'ws':
                state.discard()
                ws = True
            #
            state.skipwhitespace()
            t = state.peek()
            if t.token == 'char':
                if t.text == '>' or t.text == '+' or t.text == '~':
                    sel.rules.append(t.text)
                    state.discard()
                    continue
                if t.text == '{' or t.text == ';':
                    break
            if ws:
                sel.rules.append(' ')
                continue
        #
        if sel:
            css.rule.rules.append(sel)
        else:
            state.skipwhitespace()
            t = state.peek()
            if t.token == 'char':
                if t.text == ',':
                    state.discard()
                    continue
            #
            break

def CSSOneBlock(state):
    css = CSSBlock()
    #
    state.skipwhitespace()
    t = state.peek()
    if not t:
        return None
    #
    if t.token == 'at-keyword':
        css.atrule = CSSAtRule()
        css.atrule.name = t.text
        state.discard() # discard peek() result
        #
        subs = [ ]
        #
        while True:
            state.skipwhitespace()
            t = state.get()
            if not t:
                break
            if t.token == 'char' and t.text == ';':
                if len(subs) == 0:
                    break
            elif t.token == 'char' and t.text == '{':
                if css.atrule.name == 'font-face':
                    CSSBlockNVParse(state,css)
                    break
                elif css.atrule.name == 'layer' or css.atrule.name == 'media':
                    while True:
                        state.skipwhitespace()
                        t = state.peek()
                        if not t:
                            break
                        if t.token == 'char' and t.text == '}':
                            state.discard()
                            break
                        subcss = CSSOneBlock(state)
                        if subcss == None:
                            break
                        css.atrule.blocks.append(subcss)
                    break
                else:
                    subs.append(t.text)
            elif t.token == 'char' and t.text == '(':
                subs.append(t.text)
            elif t.token == 'char' and t.text == ')':
                if len(subs) > 0 and subs[-1] == '(':
                    subs.pop()
            elif t.token == 'char' and t.text == '}':
                if len(subs) > 0 and subs[-1] == '{':
                    subs.pop()
                    if len(subs) == 0:
                        css.atrule.tokens.append(t)
                        break
            #
            css.atrule.tokens.append(t)
        #
        return css;
    # selectors
    CSSSelectorParse(state,css)
    #
    state.skipwhitespace()
    t = state.peek()
    # block parsing
    if t.token == 'char' and t.text == '{':
        state.discard() # discard peek() result
        CSSBlockNVParse(state,css)
        return css;
    # ;
    if t.token == 'char' and t.text == ';':
        state.discard()
        return css;
    #
    raise Exception("CSS parsing error "+str(t))

def CSSmidparse(blob,state=CSSmidState()):
    state.start(blob)
    #
    while True:
        css = CSSOneBlock(state)
        if css == None:
            break
        #
        yield css

def CSSMidFancyStringPseudoClassSelector(pcs,indent=0): # pcs = CSSPseudoClassSelector
    r = ""
    #
    if not pcs.name == None:
        r += pcs.name
    if not pcs.tokens == None and len(pcs.tokens) > 0:
        r += "("
        for t in pcs.tokens:
            r += CSSMidFancyStringToken(t)
        r += ")"
    #
    return r

def CSSMidFancyStringSimpleSelector(ss,indent=0): # ss = CSSSimpleSelector
    r = ""
    #
    if not ss.typeSelector == None:
        r += ss.typeSelector
    #
    for ent in ss.classSelectors:
        r += "." + ent
    #
    for ent in ss.idSelectors:
        r += "#" + ent
    #
    for ent in ss.attrSelectors: # ent = CSSAttributeSelector
        r += "["
        r += ent.attribute
        if ent.howMatch == 'exact':
            r += "="
        elif ent.howMatch == 'any':
            r += "~="
        elif ent.howMatch == 'begin-dash':
            r += "|="
        elif ent.howMatch == 'begins':
            r += "^="
        elif ent.howMatch == 'ends':
            r += "$="
        elif ent.howMatch == 'substr':
            r += "*="
        elif ent.howMatch == None:
            True
        else:
            r += "("+ent.howMatch+")"
        if not ent.howMatch == None and not ent.value == None:
            r += ent.value
        r += "]"
    #
    for ent in ss.pseudoClassSelectors: # ent = CSSPseudoClassSelector
        r += ":"+CSSMidFancyStringPseudoClassSelector(ent,indent+1)
    #
    for ent in ss.pseudoElementSelectors: # ent = str
        r += "::"+ent
    #
    return r

def CSSMidFancyStringSelector(sel,indent=0): # sel = CSSSelector
    spc = " " * (indent*4)
    r = ""
    #
    if not sel.rules == None and len(sel.rules) > 0:
        for sr in sel.rules:
            if isinstance(sr,str):
                if not r == "":
                    r += "\n"
                r += spc + "combiner: \"" + sr + "\""
            else:
                v = CSSMidFancyStringSimpleSelector(sr,indent)
                if not r == "":
                    r += "\n"
                r += spc + "simple selector: " + v
    #
    return r

def CSSMidFancyStringMatchRule(rule,indent=0): # rule = CSSMatchRule
    spc = " " * (indent*4)
    r = ""
    #
    if not rule.rules == None and len(rule.rules) > 0:
        for subrule in rule.rules:
            v = CSSMidFancyStringSelector(subrule,indent+1)
            if not v == "":
                if not r == "":
                    r += "\n"
                r += spc + "selector:\n" + v
    #
    return r

def CSSMidFancyStringAtRule(atrule,indent=0): # atrule = CSSAtRule
    spc = " " * (indent*4)
    r = ""
    #
    if not atrule.name == None:
        if not r == "":
            r += " "
        else:
            r = spc
        r += "@" + atrule.name
    #
    if len(atrule.tokens) > 0:
        for ent in atrule.tokens:
            if not r == "":
                r += " "
            else:
                r = spc
            r += ent.text
    #
    if len(atrule.blocks) > 0:
        indent2 = indent + 1
        spc2 = " " * (indent2*4)
        for bl in atrule.blocks:
            v = CSSMidFancyStringBlock(bl,indent2+1)
            if not v == "":
                if not r == "":
                    r += "\n"
                r += spc2 + "block:\n" + v
    #
    return r

def CSSMidFancyStringToken(t):
    if t.token == 'url':
        return "url("+t.text+")"
    if t.token == 'hash':
        return "#"+t.text
    if t.token == 'class':
        return "."+t.text
    if t.token == 'function':
        return t.text+"("
    return t.text

def CSSMidFancyStringBlock(ent,indent=1): # ent = CSSBlock
    spc = " " * (indent*4)
    r = ""
    #
    if not ent.atrule == None:
        v = CSSMidFancyStringAtRule(ent.atrule,indent+1)
        if not v == "":
            if not r == "":
                r += "\n"
            r += spc + "at rule:\n" + v
    if not ent.rule == None:
        v = CSSMidFancyStringMatchRule(ent.rule,indent+1)
        if not v == "":
            if not r == "":
                r += "\n"
            r += spc + "match rule:\n" + v
    if not ent.nvlist == None and len(ent.nvlist) > 0:
        if not r == "":
            r += "\n"
        r += spc + "nvpairs:"
        indent2 = indent + 1
        spc2 = " " * (indent2*4)
        for i,(name,vl) in enumerate(ent.nvlist.items()):
            for val in vl:
                if not r == "":
                    r += "\n"
                r += spc2 + name + ":"
                if val.valueType == 'tokens':
                    for t in val.value:
                        if t.token == 'ws':
                            r += " "
                        else:
                            r += " " + CSSMidFancyStringToken(t)
                r += ";"
    if not ent.subblocklist == None and len(ent.subblocklist) > 0:
        for subent in ent.subblocklist:
            v = CSSMidFancyStringBlock(subent,indent+1)
            if not v == "":
                if not r == "":
                    r += "\n"
                r += spc + "subblock:\n" + v
    #
    return r

