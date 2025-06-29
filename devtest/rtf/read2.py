#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTF import *

inFile = sys.argv[1]
rawrtf = rawrtfloadfile(inFile)

class RTFmidReaderState:
    llstate = RTFllReaderState()
    readMode = 'unicode' # 'raw', 'ansi' or 'unicode'
    encoding = None # set by \ansi \mac \pc \pca
    codepage = None # set by \ansicpgN
    lookahead = None
    riter = None
    blob = None
    def __init__(self):
        self.lookahead = [ ]
    def fill(self,i=1):
        while len(self.lookahead) < i:
            try:
                self.lookahead.append(next(self.riter))
            except StopIteration:
                self.lookahead.append(RTFToken())
    def peek(self,i=0):
        self.fill(i+1)
        return self.lookahead[i]
    def discard(self):
        self.lookahead = self.lookahead[1:]
    def get(self):
        t = self.peek()
        self.discard()
        return t

def RTFmidParse(blob,state=RTFmidReaderState()):
    state.blob = blob
    state.riter = iter(RTFllParse(state.blob,state.llstate))
    while True:
        t = state.get()
        if not t:
            break
        #
        yield t

midrtfstate = RTFmidReaderState()
for ent in RTFmidParse(rawrtf,midrtfstate):
    print(ent)

