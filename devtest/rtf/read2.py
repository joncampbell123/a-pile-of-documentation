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
    stateStack = None
    stateInit = {
        "uc": 1,
        "inRTF": False,
        "encoding": None, # set by \ansi \mac \pc \pca
        "codepage": None  # set by \ansicpgN
    }
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
                t = next(self.riter)
                # convert token control codes as if ascii text
                if t.token == 'control' or t.token == '{' or t.token == '}' or t.token == '\\' or t.token == 'special':
                    if not t.text == None and isinstance(t.text,bytes):
                        t.text = t.text.decode('ascii')
                #
                self.lookahead.append(t)
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
    def getCharset(self):
        return 'cp1252' # Windows Western ANSI is a good default to assume

def RTFmidParseLL(blob,state=RTFmidReaderState()):
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
        elif t.token == 'control' and t.text == 'rtf':
            state.state["inRTF"] = True
        elif state.state["inRTF"] == True:
            if t.token == 'control':
                if t.text == 'ansi' or t.text == 'mac' or t.text == 'pc' or t.text == 'pca':
                    state.state['encoding'] = t.text
                elif t.text == 'ansicpg':
                    state.state['codepage'] = t.param
                elif t.text == 'uc':
                    if state.readMode == 'ansi':
                        continue # pretend to be pre-unicode reader that ignores unicode controls
                    if state.readMode == 'unicode':
                        if t.param >= 0:
                            state.state['uc'] = t.param
                        else:
                            state.state['uc'] = 1
                        continue # do not pass to caller
                elif t.text == 'u':
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
                        t.text = chr(uc)
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

def RTFcharsetToUnicode(bt,state):
    return bt.decode(state.getCharset())

def RTFmidParse(blob,state=RTFmidReaderState()):
    accumText = ''
    accumTextBin = b''
    #
    for ent in RTFmidParseLL(blob,state):
        if ent.token == 'text':
            if not ent.text == None:
                if isinstance(ent.text,bytes):
                    accumTextBin += ent.text
                elif isinstance(ent.text,str):
                    accumText += RTFcharsetToUnicode(accumTextBin,state)
                    accumText += ent.text
                    accumTextBin = b''
        else:
            if len(accumTextBin) > 0:
                accumText += RTFcharsetToUnicode(accumTextBin,state)
                accumTextBin = b''
            if len(accumText) > 0:
                n = RTFToken()
                n.token = 'text'
                n.text = accumText
                accumText = ''
                yield n
            #
            yield ent
            if not ent:
                break

midrtfstate = RTFmidReaderState()
if not fileReadMode == None:
    midrtfstate.readMode = fileReadMode
#
for ent in RTFmidParse(rawrtf,midrtfstate):
    print(ent)

