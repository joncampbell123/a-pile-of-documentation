#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docHTML import *

rawhtml = rawhtmlloadfile('unicode.xml')

llhtmlstate = HTMLllReaderState()
hiter = iter(HTMLllParse(rawhtml,llhtmlstate))

entity2unicode = { }
unicode2entity = [ { } ]

def decodedecval(v):
    # "63"
    # or maybe even "62-8402"
    seq = v.split('-')
    return ''.join(map(lambda a: chr(int(a)),seq))

def dolist(uncode,estr):
    global entity2unicode,unicode2entry
    if len(uncode) > 0 and len(estr) > 0:
        if not estr in entity2unicode:
            entity2unicode[estr] = uncode
        #
        uidx = len(uncode)
        while len(unicode2entity) <= uidx:
            unicode2entity.append({ })
        #
        if not uncode in unicode2entity[uidx]:
            unicode2entity[uidx][uncode] = estr

for ent in hiter:
    if ent.elemType == 'tag':
        if ent.tag == b'charlist' and ent.tagInfo == 'open':
            break

count = 0
for ent in hiter:
    if ent.elemType == 'tag':
        if ent.tag == b'charlist' and ent.tagInfo == 'close':
            break
        if ent.tag == b'character' and ent.tagInfo == 'open':
            uncode = None
            uncoderaw = None
            for a in ent.attr:
                if a.name == b'dec':
                    uncoderaw = a.value.decode('ascii')
                    uncode = decodedecval(uncoderaw)
            #
            count += 1
            if count >= 64 and not uncoderaw == None:
                sys.stderr.write("Processing: "+uncoderaw+"\n")
                count = 0
            #
            if not uncode == None:
                for ent in hiter:
                    if ent.tag == b'character' and ent.tagInfo == 'close':
                        break
                    if ent.tag == b'entity' and ent.tagInfo == 'open':
                        for a in ent.attr:
                            if a.name == b'id':
                                dolist(uncode,a.value.decode('ascii'))

# print it out
def strescchar(x):
    if ord(x) < 32:
        return '\\x%02x' % ord(x)
    if x == '\\' or x == '\"' or x == "\'":
        return '\\'+x
    return x

of = open("docHTMLentities.py","w",encoding="utf-8")
of.write("# auto generated, see unicode2code.py. approve and move to ../../apodlib/\n")

# emit
x = "HTMLent2u={"
count = 0
for (ent,uc) in entity2unicode.items():
    if count > 0:
        x += ","
    x += "'"+''.join(map(strescchar,ent))+"':'"+''.join(map(strescchar,uc))+"'"
    count += 1
x += "}\n"
of.write(x)

# emit
x = "HTMLu2ent=[\n"
acount = 0
for idx in range(0,len(unicode2entity)):
    d = unicode2entity[idx]
    #
    if acount > 0:
        x += ',\n'
    #
    count = 0
    x += "{"
    for (uc,ent) in d.items():
        if count > 0:
            x += ","
        x += "'"+''.join(map(strescchar,uc))+"':'"+''.join(map(strescchar,ent))+"'"
        count += 1
    x += "}"
    acount += 1
    #
x += "\n]\n"
of.write(x)

of.close()
