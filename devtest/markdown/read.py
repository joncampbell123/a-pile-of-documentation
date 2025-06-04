#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRawText import *
from apodlib.docMarkdown import *

inFile = sys.argv[1]
lines = list(tabstospacesgen(rawtexttoutf8gen(rawtextsplitlinesgen(rawtextloadfile(inFile))),4))

# parse
mdstate = MarkdownState()
mdRoot = parsemarkdown(lines,mdstate)

# dump
dumpMDstate(mdstate)
dumpMD(mdRoot)
