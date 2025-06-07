#!/usr/bin/python3

import os
import re
import sys

def rawhtmlloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTML import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

llhtmlstate = HTMLllReaderState()

sys.stdout.buffer.flush()
for ent in HTMLllParse(rawhtml,llhtmlstate):
    sys.stdout.buffer.write(HTMLllTokenToHTML(ent,llhtmlstate))

