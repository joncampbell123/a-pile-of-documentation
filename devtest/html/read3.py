#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLhi import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

hihtmlstate = HTMLhiReaderState()
HTMLhiParseAll(rawhtml,hihtmlstate)

def HTMLhiDump(state,node=None,indent=0):
    if node == None:
        node = state.getRoot()
    #
    spc = "  " * indent
    print(spc+str(node))
    for ent in node.children:
        HTMLhiDump(state,ent,indent+1)

HTMLhiDump(hihtmlstate)

print("----Info----")
print("Fixups: "+str(hihtmlstate.fixups))
print("DocType: "+str(hihtmlstate.docType))
print("HTML element: "+str(hihtmlstate.htmlElement))
print("HEAD element: "+str(hihtmlstate.headElement))
print("BODY element: "+str(hihtmlstate.bodyElement))

