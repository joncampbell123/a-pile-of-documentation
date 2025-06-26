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
    if ent.token == 'control':
        if ent.destination:
            sys.stdout.buffer.write(b'\\*')
        sys.stdout.buffer.write(b'\\'+ent.text)
        if not ent.param == None:
            sys.stdout.buffer.write(str(ent.param).encode('ascii'))
        sys.stdout.buffer.write(b' ')
    else:
        sys.stdout.buffer.write(ent.text)

