
import os
import re
import sys

from apodlib.docCSV import *

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

