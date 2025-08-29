#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRBIL import *

inFile = sys.argv[1]
encoding = 'utf-8'
if len(sys.argv) > 2:
    encoding = sys.argv[2]

rawtxt = rbilloadfile(inFile)
rbr = RBILReader(rawtxt)
for ri in rbr:
    print("=================================================")
    print("ENTRY")
    if ri.marker:
        print("Marker: '"+ri.marker+"'")
    if ri.entryIDs:
        x = ""
        for e in ri.entryIDs:
            if not x == "":
                x += ","
            x += "'"+e+"'"
        print("Entry IDs: "+x)
    print("=================================================")
    if ri.body:
        for l in ri.body:
            print("content:"+l)
    print("-------------------------------------------------")
    print("")

