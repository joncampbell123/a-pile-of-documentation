#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docCSVmid import *

inFile = sys.argv[1]
rawcsv = rawcsvloadfile(inFile)

csvr = CSVReaderState()

for csvrow in CSVmidParse(rawcsv,csvr):
    row = ""
    for cel in csvrow:
        if not row == "":
            row += ","
        row += "\"";
        for c in cel:
            if c == '\"':
                row += "\\"+c
            elif c == '\n':
                row += "\\n"
            else:
                row += c
        row += "\"";
    print("["+row+"]")

