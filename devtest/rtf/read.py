#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTF import *

inFile = sys.argv[1]
rawrtf = rawrtfloadfile(inFile)

llrtfstate = RTFllReaderState()
for ent in RTFllParse(rawrtf,llrtfstate):
    print(ent)

