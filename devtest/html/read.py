#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTML import *

inFile = sys.argv[1]
rawhtml = rawhtmlloadfile(inFile)

llhtmlstate = HTMLllReaderState()
for ent in HTMLllParse(rawhtml,llhtmlstate):
    print(ent)

print("InForm: "+str(llhtmlstate.inForm))
print("Encoding: "+str(llhtmlstate.encoding))
print("In-memory encoding: "+str(llhtmlstate.memencoding))

