#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLCSSmid import *

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

for ent in CSSmidparse(rawcss,state):
    print("----CSS block----")
    print(CSSMidFancyStringBlock(ent))

