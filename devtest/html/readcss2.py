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
        # eat whitespace here unless the next token is '.' or '#' because
        # whitespace matters to determine whether you're requiring them all
        # to match i.e. .class1.class2 to require "class1 class2" or .class1 .class2
        # that one should appear as a child to the other. Apparently .class1#id2
        # is also valid to require class="class1" and id="id2".
        #
        # it also matters, the difference between: "p.class" and "p .class"
        if t.token == 'ws':
            #
            tp = state.prev
            if not tp == None:
                if tp.token == 'char' and (tp.text == '{' or tp.text == '}' or tp.text == ':'): # if it follows these tokens there is no chance of chaining # and .
                    continue # skip
            #
            tn = state.peek()
            if tn.token == 'char' and tn.text == '.':
                yield t
            elif tn.token == 'hash':
                yield t
            continue
        # .class?
        if t.token == 'char' and t.text == '.':
            t = state.get()
            if not t:
                break
            t.token = 'class'
            yield t
            continue
        #
        yield t

for ent in CSSmidparse(rawcss,state):
    print(ent)

