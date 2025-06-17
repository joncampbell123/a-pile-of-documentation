#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTMLCSS import *

class CSSmidState:
    blob = None
    bliter = None
    llstate = None
    lookahead = None
    def __init__(self):
        self.lookahead = [ ]
        self.llstate = CSSllState()
    def start(self,blob):
        self.blob = blob
        self.bliter = iter(CSSllparse(self.blob,self.llstate))
    def peek(self,i=0):
        while len(self.lookahead) <= i:
            try:
                self.lookahead.append(next(self.bliter))
            except StopIteration:
                self.lookahead.append(CSSllToken())
        #
        return self.lookahead[i]
    def get(self):
        r = self.peek()
        self.discard()
        return r
    def discard(self,i=1):
        if i > 0:
            i -= 1
            self.peek(i)
            if len(self.lookahead) < i:
                raise Exception("OOPS")
            self.lookahead = [ ]

state = CSSmidState()

def CSSmidparse(blob,state=CSSmidState()):
    state.start(blob)
    #
    while True:
        t = state.get()
        if not t:
            break
        yield t

for ent in CSSmidparse(rawcss,state):
    print(ent)

