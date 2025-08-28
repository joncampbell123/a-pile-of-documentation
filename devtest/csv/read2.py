#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docCSV import *

inFile = sys.argv[1]
rawcsv = rawcsvloadfile(inFile)

csvr = CSVReaderState()

def CSVmidParse(rawcsv,csvr):
    row = [ ]
    for csvrecord in CSVllParse(rawcsv,csvr):
        if csvrecord == '\n':
            yield row
            row = [ ]
        else:
            row.append(csvrecord)
    #
    if len(row) > 0:
        yield row
        row = [ ]

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

