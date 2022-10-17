#!/usr/bin/python3

import os
import re
import csv
import glob
import json
import zlib
import math
import struct
import pathlib

def load_json(path):
    f = open(path,"r",encoding='utf-8')
    j = json.load(f)
    f.close()
    return j

x = load_json("x.json")
res = [ [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L" ] ]
columns = [ "value", "extended" ]
csvcolumns = [ "key" ]
csvcolumns.extend(columns)

csvf = open("x.csv","w",newline="")
csvw = csv.writer(csvf)

csvw.writerow(csvcolumns)

for key in x:
    vals = x[key]
    cols = [ key ]
    for col in columns:
        val = ""
        if col in vals:
            val = vals[col]
        cols.append(val)
    csvw.writerow(cols)

csvf.close()

