#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTFmid import *

midrtfstate = RTFmidReaderState()
if not fileReadMode == None:
    midrtfstate.readMode = fileReadMode
#
for ent in RTFmidParse(rawrtf,midrtfstate):
    print(ent)

