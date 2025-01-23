#!/usr/bin/python3

import os
import re
import sys
import csv

sbcs_cnv = None
input_file = None
output_file = None

it = iter(sys.argv)
next(it) # skip argv

try:
    while True:
        a = next(it)
        if a[0] == '-':
            while a[0] == '-':
                a = a[1:]
            if a == "i":
                input_file = next(it)
            elif a == "o":
                output_file = next(it)
            elif a == "csv":
                sbcs_cnv = next(it)
            elif a == "h" or a == "help":
                print(" -i <input file>")
                print(" -o <output file>");
                print(" -csv <code page csv>")
                sys.exit(1)
            else:
                raise Exception("Unknown switch")
        else:
            raise Exception("Unexpected")
except StopIteration:
    True

if input_file == None or output_file == None or sbcs_cnv == None:
    raise Exception("Input, output, and sbcs files required. See --help")

#------------------------------------------------------------

sbcs_map = [ None ] * 256
sbcs_f = open(sbcs_cnv,encoding='utf-8')
sbcs_cr = csv.reader(sbcs_f)
for row in sbcs_cr:
    if len(row) < 8:
        continue
    # ['Code (hexadecimal)', 'Code (decimal)', 'Code (octal)', 'Code (binary)', 'Unicode code point', 'name', 'description', 'display']
    # ['e2', '226', '342', '11100010', '0393', 'GREEK CAPITAL LETTER GAMMA', '', 'Γ']
    #   hex   dec    oct    binary      ucode  desc                               char
    #   0     1      2      3           4      5                             6    7
    bv = row[1].strip()
    if not re.match(r"[0-9]+",bv):
        continue
    bv = int(bv)
    #
    dc = row[7]
    if dc == "":
        continue
    #
    if not sbcs_map[bv] == None:
        raise Exception("SBCS code redefined")
    sbcs_map[bv] = dc
sbcs_f.close()

for i in range(0,256):
    if sbcs_map[i] == None:
        sys.stderr.write("WARNING: SBCS map does not define "+str(i)+"\n")

fi = open(input_file,mode="rb")
fo = open(output_file,encoding="utf-8",mode="w")
for lin_in in fi:
    lin_out = ""
    for b in lin_in:
        c = sbcs_map[b]
        if b == 13 or b == 10:
            lin_out += chr(b)
        elif not c == None and not c == "":
            lin_out += c
    fo.write(lin_out)
fi.close()
fo.close()
