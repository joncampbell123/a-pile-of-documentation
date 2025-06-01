#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

def markdownconvlines(lines):
    r = [ ]
    for line in lines:
        r.append(line.decode('utf-8'))
    return r

inFile = sys.argv[1]
rawmd = markdownconvlines(rawtextsplitlines(rawtextloadfile(inFile)))
print(rawmd)

