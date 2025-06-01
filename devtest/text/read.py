#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

inFile = sys.argv[1]
encoding = 'utf-8'
if len(sys.argv) > 2:
    encoding = sys.argv[2]

rawtxt = rawtextloadfile(inFile)

print("-----RAW-----")
for line in rawtextsplitlines(rawtxt):
    print(b"Line> \""+line+b"\" <eol>")

print("-----"+encoding+"-----")

dosplitline = rawtextsplitlines
if encoding == 'utf-16le' or encoding == 'utf_16_le':
    dosplitline = rawtextsplitlines16le
elif encoding == 'utf-16be' or encoding == 'utf_16_be':
    dosplitline = rawtextsplitlines16be

for rawline in dosplitline(rawtxt):
    try:
        line = rawline.decode(encoding)
        print("Line> \""+line+"\" <eol>")
    except:
        print("Line> (failed to decode)")

