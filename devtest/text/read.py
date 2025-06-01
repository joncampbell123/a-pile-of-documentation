#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

inFile = sys.argv[1]

rawtxt = rawtextloadfile(inFile)

print("-----RAW-----")
for line in rawtextsplitlines(rawtxt):
    print(b"Line> \""+line+b"\" <eol>")

print("-----UTF-8-----")
for rawline in rawtextsplitlines(rawtxt):
    try:
        line = rawline.decode('utf-8')
        print("Line> \""+line+"\" <eol>")
    except:
        print("Line> (failed to decode)")

