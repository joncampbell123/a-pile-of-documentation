#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLCSSmid import *

for ent in CSSmidparse(rawcss,state):
    print("----CSS block----")
    print(ent)

