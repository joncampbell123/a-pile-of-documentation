#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

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

class CSSSimpleSelector:
    pseudoClassSelectors = None
    classSelectors = None
    attrSelectors = None
    typeSelector = None
    idSelectors = None
    def __init__(self):
        self.pseudoClassSelectors = [ ]
        self.classSelectors = [ ]
        self.attrSelectors = [ ]
        self.idSelectors = [ ]
    def __bool__(self):
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
                t = state.peek()
                if t.token == 'ident' or t.token == 'string':
                    attr.value = t.text
                    state.discard()
                else:
                    raise Exception("CSS attribute selector expected value "+str(t))
            #
            t = state.peek()
            if t.token == 'char' and t.text == ']':
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
            if t.token == 'ident':
                ss.pseudoClassSelectors.append(t.text)
                state.discard() # discard :
                state.discard() # discard ident
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
    tokens = None
    def __init__(self):
        self.tokens = [ ]
    def __str__(self):
        r = "[CSSAtRule"
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
        return r;

class CSSMatchRule:
    atrule = None # CSSAtRule
    rules = None # CSSSelector
    def __init__(self):
        self.atrule = None
        self.rules = [ ]
    def __str__(self):
        r = "[CSSMatchRule"
        if not self.atrule == None:
            r += " atrule="
            r += str(self.atrule)
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
    valueType = None # 'block'=CSSBlock 'tokens'=list of tokens
    def __str__(self):
        r = "[CSSNameValue"
        if not self.name == None:
            r += " name="+self.name
        if not self.valueType == None:
            r += " valueType="+self.valueType
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
    rule = None # CSSMatchRule
    nvlist = None # CSSNameValue
    def __init__(self):
        self.rule = CSSMatchRule()
        self.nvlist = { }
    def __str__(self):
        r = "[CSSBlock"
        if not self.rule == None:
            r += " rule="
            r += str(self.rule)
        if not self.nvlist == None:
            r += " nv=("
            c = 0
            for i,(name,val) in enumerate(self.nvlist.items()):
                if c > 0:
                    r += " "
                r += str(name)+":"+str(val)
                c += 1
            r += ")"
        r += "]"
        return r

def CSSBlockNVParse(state,css): # CSSBlock
    # already took { token
    while True:
        state.skipwhitespace()
        nv = CSSNameValue()
        t = state.get()
        if not t:
            break
        if t.token == 'char' and t.text == '}':
            break
        # name
        if t.token == 'ident':
            nv.name = t.text
        else:
            raise Exception("CSS parsing error expect name")
        # value
        state.skipwhitespace()
        t = state.get()
        if not t:
            break
        if t.token == 'char' and t.text == ':':
            nv.valueType = 'tokens'
            nv.value = [ ]
            while True:
                state.skipwhitespace()
                t = state.get()
                if t.token == 'char' and t.text == ';':
                    break
                if not t:
                    break
                nv.value.append(t)
        else:
            raise Exception("CSS parsing error expect colon+value")
        #
        css.nvlist[nv.name] = nv

def CSSmidparse(blob,state=CSSmidState()):
    state.start(blob)
    #
    while True:
        state.skipwhitespace()
        css = CSSBlock()
        t = state.peek()
        if not t:
            break
        #
        if t.token == 'at-keyword':
            css.rule.atrule = CSSAtRule()
            css.rule.atrule.name = t.text
            state.discard() # discard peek() result
            #
            while True:
                state.skipwhitespace()
                t = state.get()
                if t.token == 'char' and t.text == ';':
                    break
                #
                css.rule.atrule.tokens.append(t)
            #
            yield css;
            continue
        # selectors
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
                    if t.text == '>' or t.text == '+':
                        sel.rules.append(t.text)
                        state.discard()
                        continue
                    if t.text == '{' or t.text == ';':
                        break
                if ws:
                    sel.rules.append(' ')
                    continue
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
        #
        state.skipwhitespace()
        t = state.peek()
        # block parsing
        if t.token == 'char' and t.text == '{':
            state.discard() # discard peek() result
            CSSBlockNVParse(state,css)
            yield css;
            continue
        # ;
        if t.token == 'char' and t.text == ';':
            state.discard()
            yield css;
            continue
        #
        raise Exception("CSS parsing error "+str(t))

for ent in CSSmidparse(rawcss,state):
    print(ent)

