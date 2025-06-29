#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTFmid import *

inFile = sys.argv[1]
if len(sys.argv) > 2:
    fileReadMode = sys.argv[2]
    if not fileReadMode == 'raw' and not fileReadMode == 'unicode' and not fileReadMode == 'ansi':
        raise Exception("File read mode must be raw, unicode, or ansi")
else:
    fileReadMode = None
#
rawrtf = rawrtfloadfile(inFile)

midrtfstate = RTFmidReaderState()
if not fileReadMode == None:
    midrtfstate.readMode = fileReadMode
#
for ent in RTFmidParse(rawrtf,midrtfstate):
    print(ent)

