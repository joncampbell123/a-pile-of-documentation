
import os
import sys

from apodlib.docRawText import *

def rbilloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

# eight '-' then a marker char, more '-', the unique ID, trailing '-'
# --------!---CONTACT_INFO---------------------
# --------m-02----SI0714-----------------------
# ----------P0000001F--------------------------

class RBILReader:
    currentLine = None
    lineIter = None
    #
    class entry:
        entryIDs = None
        marker = None
        body = None
        def __init__(self):
            self.body = [ ]
    #
    def __init__(self,blob):
        self.lineIter = iter(rawtextsplitlinesgen(blob))
    def isDividerLine(self,cr):
        if not cr == None:
            if cr[0:8] == "--------":
                return True
        #
        return False
    def getCurrentLine(self):
        if self.currentLine == None:
            try:
                self.currentLine = next(self.lineIter).decode('utf-8')
            except StopIteration:
                return None
        #
        return self.currentLine
    def gotoNextLine(self):
        self.currentLine = None
    def read(self):
        while True:
            cr = self.getCurrentLine()
            if cr == None:
                return None
            if cr.strip() == '':
                self.gotoNextLine()
                continue
            break
        #
        r = RBILReader.entry()
        #
        cr = self.getCurrentLine()
        if cr == None:
            return None
        if self.isDividerLine(cr):
            # 8th position is the marker, if any
            cr = cr[8:]
            if len(cr) > 0 and not cr[0] == '-':
                r.marker = cr[0];
                cr = cr[1:]
            while len(cr) > 0 and cr[0] == '-':
                cr = cr[1:]
            r.entryIDs = re.split(r'--+',cr)
            while len(r.entryIDs) > 0 and r.entryIDs[-1] == '':
                r.entryIDs.pop()
        else:
            r.body.append(cr)
        #
        self.gotoNextLine()
        #
        while True:
            cr = self.getCurrentLine()
            if cr == None:
                break
            if self.isDividerLine(cr):
                break
            #
            r.body.append(cr)
            self.gotoNextLine()
        #
        return r
    def __iter__(self):
        while True:
            x = self.read()
            if x == None:
                break
            yield x

