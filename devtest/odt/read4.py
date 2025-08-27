#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIPhigh import *

inFile = sys.argv[1]

def opendirenum(zr,path=None):
    if path == None:
        path = ""
    #
    for x in zr.opendir(path):
        print(x)
        if x.dtype == 'dir':
            opendirenum(zr,path+"/"+x.dname)

zr = ZIPHighReader(inFile)
zr.scan()
zr.dbg_dump_dirs()
opendirenum(zr)
zr.close()

