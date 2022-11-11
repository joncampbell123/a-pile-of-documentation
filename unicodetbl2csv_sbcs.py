#!/usr/bin/python3

import os
import re
import sys

sfile = None
dfile = None

ai = iter(sys.argv)
# first one is the name of the Python script
next(ai)
# parse
try:
    while True:
        a = next(ai)
        if a[0:2] == "--":
            what = a[2:]
            if what == "in":
                sfile = next(ai)
            elif what == "out":
                dfile = next(ai)
            else:
                raise Exception("Unexpected switch "+what)
        else:
            raise Exception("Unexpected arg "+a)
except StopIteration:
    True

if sfile == None or dfile == None:
    raise Exception("Source and dest files must be specified with --in <file> and --out <file>")

s = open(sfile,"r",encoding="ascii")
d = open(dfile,"w",encoding="utf-8")

print("charcode,name,character,comments",file=d)

for line in s:
    line = line.strip()
    if line[0] == '#':
        continue
    # ex: "0x02	0x0002	#START OF TEXT"
    # also the files use \t not space, which means if you edit this
    # in some text editors you may lose the ability to parse this
    # if they replace tab with spaces
    x = line.split('\t')
    # [ inbyte outchar #name ]
    if len(x) == 2:
        x.append("#")
    if len(x) < 3:
        continue
    if x[2][0] == '#':
        x[2] = x[2][1:]
    inbyte = int(x[0],base=16)
    outchar = int(x[1],base=16)
    name = x[2]
    if inbyte < 0x20: # the Wikipedia list takes care of this case, the list treats this range as ASCII control chars
        continue
    outcharstr = chr(outchar)
    if outcharstr == "\"":
        outcharstr = "\"\"" # escape for CSV
    print(hex(inbyte)+",\""+name+"\",\""+outcharstr+"\",",file=d)

s.close()
d.close()

