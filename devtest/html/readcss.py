#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docBOM import *

# low level reader:
# returns a flat sequence of HTML tags, or text.
# concerns itself only with whether the text is UTF-16 or not.
# it's up to you to turn the stream of tags into a DOM hierarchy and convert from whatever charset to UTF-8.

def rawcssloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

inFile = sys.argv[1]
rawcss = rawcssloadfile(inFile)

