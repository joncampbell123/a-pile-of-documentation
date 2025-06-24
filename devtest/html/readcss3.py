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
            if not t.text == None:
                r += t.text
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
    for ent in ss.attrSelectors:
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
    for ent in ss.pseudoClassSelectors:
        r += ":"+CSSMidFancyStringPseudoClassSelector(ent,indent+1)
    #
    for ent in ss.pseudoElementSelectors:
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

def CSSMidFancyString(ent,indent=1): # ent = CSSBlock
    spc = " " * (indent*4)
    r = ""
    #
    if not ent.rule == None:
        v = CSSMidFancyStringMatchRule(ent.rule,indent+1)
        if not v == "":
            if not r == "":
                r += "\n"
            r += spc + "match rule:\n" + v
    #
    return r

for ent in CSSmidparse(rawcss,state):
    print("----CSS block----")
    print(CSSMidFancyString(ent))

