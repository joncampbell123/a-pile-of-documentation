#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docCSV import *

inFile = sys.argv[1]
rawcsv = rawcsvloadfile(inFile)

csvr = CSVReaderState()

for csvrecord in CSVllParse(rawcsv,csvr):
    if csvrecord == "\n":
        print("\\n")
    else:
        print("\""+csvrecord+"\"")

