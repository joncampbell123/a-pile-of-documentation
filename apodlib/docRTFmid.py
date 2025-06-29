
import os
import re
import sys

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
        "mode": None,
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
        if self.state['encoding'] == 'ansi':
            if not self.state['codepage'] == None and self.state['codepage'] > 0:
                return 'cp'+str(self.state['codepage']) # i.e. \ansicpg1252 -> cp1252
            #
            return 'cp1252' # Windows Western ANSI is a good default to assume
        if self.state['encoding'] == 'mac':
            return 'mac'
        if self.state['encoding'] == 'pc':
            return 'cp437'
        if self.state['encoding'] == 'pca':
            return 'cp850'
        #
        return 'cp1252' # Windows Western ANSI is a good default to assume
    def initAccumText(self):
        self.accumText = ''
        self.accumTextBin = b''
    def addAccumText(self,text):
        if isinstance(text,bytes):
            self.accumTextBin += text
        elif isinstance(text,str):
            self.accumText += RTFcharsetToUnicode(self.accumTextBin,self)
            self.accumText += text
            self.accumTextBin = b''
    def getAccumText(self):
        if len(self.accumTextBin) > 0:
            self.accumText += RTFcharsetToUnicode(self.accumTextBin,self)
            self.accumTextBin = b''
        if len(self.accumText) > 0:
            r = self.accumText
            self.accumText = ''
            return r
        #
        return None

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
            t.stackDepth = len(state.stateStack)
        elif t.token == '}':
            state.popstate()
            t.stackDepth = len(state.stateStack)
        elif t.token == 'control' and t.text == 'rtf':
            state.state["inRTF"] = True
        elif state.state["inRTF"] == True:
            # \upr in ansi mode: do not pass tokens if unicode reading
            if state.state['mode'] == 'upr:ansi':
                if t.token == 'control' and t.text == 'ud' and t.destination == True:
                    state.state['mode'] = 'upr:unicode'
                    continue # do not pass
                else:
                    if state.readMode == 'unicode':
                        continue # do not pass
            # \upr in unicode mode (having read the \*\ud control code): do not pass tokens if ansi reading
            elif state.state['mode'] == 'upr:unicode':
                if state.readMode == 'ansi':
                    continue # do not pass
            #
            if t.token == 'control':
                if t.text == 'ansi' or t.text == 'mac' or t.text == 'pc' or t.text == 'pca':
                    state.state['encoding'] = t.text
                elif t.text == 'ansicpg':
                    state.state['codepage'] = t.param
                elif t.text == 'upr':
                    state.state['mode'] = 'upr:ansi'
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
                        skip = state.state['uc']
                        while t.token == 'text':
                            cut = skip
                            if cut > len(t.text):
                                cut = len(t.text)
                            skip = skip - cut
                            # truncate bytes according to cut, remove text token entirely if no text left
                            t.text = t.text[cut:]
                            if len(t.text) == 0:
                                state.discard()
                            else:
                                break
                            # next!
                            t = state.peek()
                        continue
        #
        yield t

def RTFcharsetToUnicode(bt,state):
    return bt.decode(state.getCharset())

def RTFmidParse(blob,state=RTFmidReaderState()):
    state.initAccumText()
    #
    for ent in RTFmidParseLL(blob,state):
        if ent.token == 'text':
            if not ent.text == None:
                state.addAccumText(ent.text)
        else:
            r = state.getAccumText()
            if not r == None:
                n = RTFToken()
                n.token = 'text'
                n.text = r
                yield n
            #
            yield ent
            if not ent:
                break
    #
    r = state.getAccumText()
    if not r == None:
        n = RTFToken()
        n.token = 'text'
        n.text = r
        yield n

