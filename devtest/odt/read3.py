#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIPmid import *

inFile = sys.argv[1]

zr = ZIPMidReader(inFile)
zr.scan()
#
print("**DIR**")
for ent in zr.readdir():
    print(ent)
#
print("**PATHS**")
for name in zr.readpaths():
    print(name)
#
print("**LOOKUPS**")
for name in zr.readpaths():
    print(name)
    lu = zr.lookup(name)
    print(lu)
#
print("**OPEN-BY-NAME**")
for name in zr.readpaths():
    print("* OPEN "+str(name))
    lu = zr.lookup(name)
    print("* LOOKUP "+str(lu))
    f = zr.open(name)
    if f:
        b = f.read()
        print(b)
        del f
    else:
        print("!! FAILED TO OPEN !!")
#
print("**OPEN-BY-OBJ**")
for name in zr.readpaths():
    print("* OPEN "+str(name))
    lu = zr.lookup(name)
    print("* LOOKUP "+str(lu))
    f = zr.open(lu)
    if f:
        b = f.read()
        print(b)
        del f
    else:
        print("!! FAILED TO OPEN !!")
#
zr.close()

