#!/usr/bin/python3

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRBIL import *

inFile = sys.argv[1]
encoding = 'utf-8'
if len(sys.argv) > 2:
    encoding = sys.argv[2]

class RBILmidProc:
    def __init__(self):
        True
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
            name = "InputRegs"
            while len(ri.body) > 0:
                if ri.body[0].strip() == '':
                    ri.body.pop(0)
                    continue
                x = re.match(r' *[a-zA-Z\:]+ +(=|->) +',ri.body[0])
                if x:
                    en = x.span()[0]
                    #
                    what = [ ri.body[0][en:] ]
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
                        what.append(ri.body[0][en:])
                        ri.body.pop(0)
                    #
                    if not ri.sections:
                        ri.sections = { }
                    sec = ri.sections
                    if not name in sec:
                        sec[name] = what
                    else:
                        for l in what:
                            sec[name].append(l)
                else:
                    break
        # something: etc
        #
        #   etc blah blah                            <- block 1
        #     blah                                   <- block 1
        #   etc more blah                            <- block 2
        if ri.marker == '!':
            True
        else:
            i = 0
            while i < len(ri.body):
                if ri.body[i].strip() == '':
                    i += 1
                    continue
                x = re.match(r'^([a-zA-Z0-9]+): *',ri.body[i])
                if x:
                    name = x.group(1)
                    en = x.span()[1]
                    #
                    what = [ ri.body[i][en:] ]
                    ri.body.pop(i)
                    #
                    while i < len(ri.body):
                        if ri.body[i].strip() == '':
                            break
                        x = re.match(r'^([a-zA-Z0-9]+): *',ri.body[i])
                        if x:
                            break
                        if en > 0:
                            if not ri.body[i][0:en] == (' '*en):
                                break
                        what.append(ri.body[i][en:])
                        ri.body.pop(i)
                    #
                    if not ri.sections:
                        ri.sections = { }
                    sec = ri.sections
                    if not name in sec:
                        sec[name] = what
                    else:
                        if name == 'SeeAlso':
                            True
                        else:
                            sec[name].append(True)
                        #
                        for l in what:
                            sec[name].append(l)
                else:
                    i += 1
        # empty lines
        while len(ri.body) > 0 and ri.body[0].strip() == '':
            ri.body.pop(0)

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
    if ri.sections:
        for name in ri.sections:
            print("Section '"+name+"':")
            sec = ri.sections[name]
            if sec:
                for lin in sec:
                    if lin == True:
                        print("   +---------------------")
                    else:
                        print("   |"+lin)
    print("=================================================")
    if ri.body:
        for l in ri.body:
            print("   |"+l)
    print("-------------------------------------------------")
    print("")

