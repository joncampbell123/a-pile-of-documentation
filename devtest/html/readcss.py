#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLCSS import *

inFile = sys.argv[1]
rawcss = rawcssloadfile(inFile)

state = CSSllState()

for ent in CSSllparse(rawcss,state):
    print(ent)

