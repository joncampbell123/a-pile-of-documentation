#!/usr/bin/python3

import os
import re
import sys

inFile = sys.argv[1]

def splitlines(blob):
    return re.split(b'\n\r|\r\n|\r|\n',blob)

f = open(inFile,"rb")
rawtxt = f.read()
f.close()

print("-----RAW-----")
for line in splitlines(rawtxt):
    print(b"Line> \""+line+b"\" <eol>")

print("-----UTF-8-----")
for rawline in splitlines(rawtxt):
    try:
        line = rawline.decode('utf-8')
        print("Line> \""+line+"\" <eol>")
    except:
        print("Line> (failed to decode)")

