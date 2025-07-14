#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIP import *

inFile = sys.argv[1]

zr = ZIPReader(inFile)
#
for ze in zr.readall():
    print(ze)
    zf = zr.open(ze)
    if not zf == None:
        b = zf.read()
        print("Length "+str(zf.size())+"/"+str(len(b)))
        print("Data: "+str(b))
        if not zf.size() == len(b):
            print("WARNING: Size mismatch")
#
zr.close()

