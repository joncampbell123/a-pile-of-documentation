#!/usr/bin/python3

import os
import sys
import zlib
import struct

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docZIP import *

inFile = sys.argv[1]

zr = ZIPReader(inFile)
zr.startFromEnd() # start reading from EndOfCentralDirectory
ze = zr.read() # should be ZIPEndOfCentralDirectory
if not ze == None:
    print(ze)
    if isinstance(ze,ZIPEndOfCentralDirectory):
        fs = ze.offsetOfStartOfCentralDirectoryWithRespectToTheStartingDiskNumber
        fe = fs + ze.sizeOfTheCentralDirectory
        zr.seek(fs)
        while zr.tell() < fe:
            ze = zr.read()
            if ze == None:
                break
            print(ze)
            #
            zf = zr.open(ze)
            if not zf == None:
                b = zf.read()
                if not b == None:
                    print("Length "+str(zf.size())+"/"+str(len(b)))
                    print("Data: "+str(b))
                    if not zf.size() == len(b):
                        print("WARNING: Size mismatch")
#
zr.close()

