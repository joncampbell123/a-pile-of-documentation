#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLmid import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

midhtmlstate = HTMLmidReaderState()
for ent in HTMLmidParse(rawhtml,midhtmlstate):
    print(ent)

print("Encoding: "+str(midhtmlstate.encoding))
print("Doctype: "+str(midhtmlstate.doctype))
print("Doctype DTD: "+str(midhtmlstate.dtd))
