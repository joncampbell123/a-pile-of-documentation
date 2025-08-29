#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docOpenDocument import *

inFile = sys.argv[1]

zr = OpenDocumentReader(inFile)
zr.dbg_dump()
zr.close()

