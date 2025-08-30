#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRBIL import *

inFile = sys.argv[1]
encoding = 'utf-8'
if len(sys.argv) > 2:
    encoding = sys.argv[2]

class RBILmidSection:
    name = None
    lines = None
    def __init__(self):
        self.lines = [ ]
    def lstriplines(self):
        minx = None
        for lin in self.lines:
            tlin = lin.rstrip()
            if len(tlin) > 0:
                x = re.match(r'^ *',tlin)
                if x:
                    nx = x.span()[1]
                    if minx == None:
                        minx = nx
                    elif minx > nx:
                        minx = nx
        if not minx == None and minx > 0:
            for i in range(0,len(self.lines)):
                if not self.lines[i][0:minx] == (' '*minx):
                    raise Exception("OOPS")
                self.lines[i] = self.lines[i][minx:]

class RBILmidProc:
    def fillin(self,ri):
        # first line starts with INT / PROC / etc.
        if ri.title == None and len(ri.body) > 0:
            x = re.match(r'^(INT|PORT|MEM|MSR|I2C) ',ri.body[0])
            if x:
                # group(1) = INT|PORT|etc..
                ri.entryType = x.group(1)
                ri.title = ri.body.pop(0)
                # empty lines
                while len(ri.body) > 0 and ri.body[0].strip() == '':
                    ri.body.pop(0)
        # INT input registers
        if not ri.marker == '!' and ri.entryType == 'INT':
            # AX = 3902h
            # DS:BX = 2111h
            sec = RBILmidSection()
            sec.name = "InputRegs"
            while len(ri.body) > 0:
                if ri.body[0].strip() == '':
                    ri.body.pop(0)
                    continue
                x = re.match(r' *[a-zA-Z\:]+ +(=|->) +',ri.body[0])
                if x:
                    en = x.span()[0]
                    #
                    sec.lines.append(ri.body[0][en:])
                    ri.body.pop(0)
                    #
                    while len(ri.body) > 0:
                        if ri.body[0].strip() == '':
                            break
                        x = re.match(r' *[a-zA-Z\:]+ +(=|->) +',ri.body[0])
                        if x:
                            break
                        x = re.match(r'^([a-zA-Z0-9]+): *',ri.body[0])
                        if x:
                            break
                        if en > 0:
                            if not ri.body[0][0:en] == (' '*en):
                                break
                        sec.lines.append(ri.body[0][en:])
                        ri.body.pop(0)
                    #
                else:
                    break
            #
            if len(sec.lines) > 0:
                sec.lstriplines()
                ri.body.insert(0,sec)
        # something: etc
        #
        #   etc blah blah                            <- block 1
        #     blah                                   <- block 1
        #   etc more blah                            <- block 2
        if ri.marker == '!':
            True
        else:
            i = 0
            sec = RBILmidSection()
            while i < len(ri.body):
                if not isinstance(ri.body[i],str):
                    i += 1
                    continue
                if ri.body[i].strip() == '':
                    i += 1
                    continue
                x = re.match(r'^([a-zA-Z0-9]+): *',ri.body[i])
                if x:
                    sec = RBILmidSection()
                    sec.name = x.group(1)
                    en = x.span()[1]
                    #
                    sec.lines = [ ri.body[i][en:] ]
                    ri.body.pop(i)
                    # if it's something like
                    # something:
                    # abc
                    # abc
                    #
                    # rather than:
                    # something: abc abc
                    if sec.lines[0] == '':
                        sec.lines.pop(0)
                        en = 0
                    #
                    while i < len(ri.body):
                        if ri.body[i].strip() == '':
                            break
                        x = re.match(r'^([a-zA-Z0-9]+): *',ri.body[i])
                        if x:
                            break
                        if en > 0:
                            if en > 8:
                                x = re.match(r'^ +',ri.body[i])
                                if x:
                                    lx = x.span()[1]
                                    if lx >= 8 and en > lx:
                                        en = lx
                            if not ri.body[i][0:en] == (' '*en):
                                break
                        sec.lines.append(ri.body[i][en:])
                        ri.body.pop(i)
                    #
                    sec.lstriplines()
                    ri.body.insert(i,sec)
                    i += 1
                else:
                    i += 1

rawtxt = rbilloadfile(inFile)
rbr = RBILReader(rawtxt)
rbmf = RBILmidProc()
for ri in rbr:
    rbmf.fillin(ri)
    print("=================================================")
    print("ENTRY")
    if ri.marker:
        print("Marker: '"+ri.marker+"'")
    if ri.entryIDs:
        x = ""
        for e in ri.entryIDs:
            if not x == "":
                x += ","
            x += "'"+e+"'"
        print("Entry IDs: "+x)
    if ri.entryType:
        print("Entry type: "+ri.entryType)
    if ri.title:
        print("Title: "+ri.title)
    print("=================================================")
    if ri.body:
        for l in ri.body:
            if isinstance(l,RBILmidSection):
                print(l.name+":")
                for lin in l.lines:
                    print("   >"+lin)
            else:
                print("   |"+l)
    print("-------------------------------------------------")
    print("")

