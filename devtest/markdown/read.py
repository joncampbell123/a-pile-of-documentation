#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *

inFile = sys.argv[1]
for line in rawtexttoutf8gen(rawtextsplitlinesgen(rawtextloadfile(inFile))):
    print(line)

