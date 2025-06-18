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
    comments = None
    prev = None # warning: prev token returned by get()
    last = None # warning: last token returned by get()
    def __init__(self):
        self.comments = [ ]
        self.lookahead = [ ]
        self.llstate = CSSllState()
    def start(self,blob):
        self.blob = blob
        self.bliter = iter(CSSllparse(self.blob,self.llstate))
    def peek(self,i=0):
        while len(self.lookahead) <= i:
            try:
                t = next(self.bliter)
                if t.token == 'comment':
                    self.comments.append(t)
                elif t.token == 'ws': # append the 'ws' token, then pull additional tokens and loop while they are 'ws'
                    self.lookahead.append(t)
                    while True:
                        t = next(self.bliter)
                        if t.token == 'comment': # skip comments as we go
                            continue
                        elif not t.token == 'ws': # if not 'ws' then stop, else just ignore it
                            self.lookahead.append(t)
                            break
                else:
                    self.lookahead.append(t)
            except StopIteration:
                self.lookahead.append(CSSllToken())
        #
        return self.lookahead[i]
    def get(self):
        self.prev = self.last
        self.last = r = self.peek()
        self.discard()
        return r
    def discard(self): # TODO: Add second parameter i if multiple token discard is ever needed
        self.peek() # fill lookahead
        #
        if len(self.lookahead) < 1:
            raise Exception("OOPS")
        #
        self.lookahead = self.lookahead[1:]

inFile = sys.argv[1]
rawcss = rawcssloadfile(inFile)

state = CSSmidState()

def CSSmidparse(blob,state=CSSmidState()):
    state.start(blob)
    #
    while True:
        t = state.get()
        if not t:
            break
        #
        yield t

for ent in CSSmidparse(rawcss,state):
    print(ent)

