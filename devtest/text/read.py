#!/usr/bin/python3

import os
import re
import sys

inFile = sys.argv[1]

def splitlines(blob):
    return re.split(b'\n\r|\r\n|\r|\n',blob)

f = open(inFile,"rb")
for line in splitlines(f.read()):
    print(b"Line> \""+line+b"\" <eol>")
f.close()

