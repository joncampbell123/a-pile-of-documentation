#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTF import *

inFile = sys.argv[1]
if len(sys.argv) > 2:
    fileReadMode = sys.argv[2]
    if not fileReadMode == 'raw' and not fileReadMode == 'unicode' and not fileReadMode == 'ansi':
        raise Exception("File read mode must be raw, unicode, or ansi")
else:
    fileReadMode = None
#
rawrtf = rawrtfloadfile(inFile)

class RTFmidReaderState:
    llstate = RTFllReaderState()
    readMode = 'unicode' # 'raw', 'ansi' or 'unicode'
    encoding = None # set by \ansi \mac \pc \pca
    codepage = None # set by \ansicpgN
    stateStack = None
    stateInit = { "uc": 1, "inRTF": False }
    state = None
    lookahead = None
    riter = None
    blob = None
    def __init__(self):
        self.lookahead = [ ]
        self.stateStack = [ ]
        self.state = self.stateInit.copy()
    def pushstate(self):
        self.stateStack.append(self.state.copy())
    def popstate(self):
        if len(self.stateStack) > 0:
            self.state = self.stateStack.pop()
        else:
            self.state = self.stateInit.copy()
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
        if t.token == '{':
            state.pushstate()
        elif t.token == '}':
            state.popstate()
        elif t.token == 'control' and t.text == b'rtf' and t.param == 1:
            state.state["inRTF"] = True
        elif state.state["inRTF"] == True:
            if t.token == 'control':
                if t.text == b'ansi' or t.text == b'mac' or t.text == b'pc' or t.text == b'pca':
                    state.encoding = t.text.decode('ascii')
                elif t.text == b'ansicpg':
                    state.codepage = t.param
                elif t.text == b'uc':
                    if state.readMode == 'ansi':
                        continue # pretend to be pre-unicode reader that ignores unicode controls
                    if state.readMode == 'unicode':
                        if t.param >= 0:
                            state.state['uc'] = t.param
                        else:
                            state.state['uc'] = 1
                        continue # do not pass to caller
                elif t.text == b'u':
                    if state.readMode == 'ansi':
                        continue # pretend to be pre-unicode reader that ignores unicode controls
                    if state.readMode == 'unicode':
                        # pass to caller as char
                        # note that because params in RTF are 16-bit signed, the unicode code point value
                        # is encoded as a NEGATIVE number if above 0x7FFF. Yechh.
                        uc = 0
                        if not t.param == None:
                            uc = t.param
                            if uc < 0:
                                uc += 0x10000
                                if uc < 0:
                                    uc = 0
                        #
                        t.token = 'text'
                        t.text = chr(uc).encode('utf-8')
                        t.param = None
                        yield t
                        # and then we have to use the last \ucN value to skip over the next N "bytes" of text.
                        # if the next token is text, peek() and modify the token in place to chop off the first N "bytes"
                        # so that next loop iteration, the truncated text is handled normally
                        t = state.peek()
                        if t.token == 'text':
                            skip = state.state['uc']
                            if skip > len(t.text):
                                skip = len(t.text)
                            t.text = t.text[skip:]
                            if len(t.text) == 0: # if truncation removes all the text, discard the token entirely and continue to next
                                state.discard()
                        continue
        #
        yield t

midrtfstate = RTFmidReaderState()
if not fileReadMode == None:
    midrtfstate.readMode = fileReadMode
#
for ent in RTFmidParse(rawrtf,midrtfstate):
    print(ent)

