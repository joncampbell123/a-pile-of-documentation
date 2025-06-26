#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTF import *

inFile = sys.argv[1]
rawrtf = rawrtfloadfile(inFile)

llrtfstate = RTFllReaderState()
controlspc = False
for ent in RTFllParse(rawrtf,llrtfstate):
    if ent.token == 'control':
        if ent.destination:
            sys.stdout.buffer.write(b'\\*')
        sys.stdout.buffer.write(b'\\'+ent.text)
        if not ent.param == None:
            sys.stdout.buffer.write(str(ent.param).encode('ascii'))
        controlspc = True
    else:
        if controlspc:
            controlspc = False
            if re.match(b'[a-zA-Z0-9\- ]',ent.text):
                sys.stdout.buffer.write(b' ')
        sys.stdout.buffer.write(ent.text)

