#!/usr/bin/python3

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__),'..','..'))

from apodlib.docRTF import *

inFile = sys.argv[1]
rawrtf = rawrtfloadfile(inFile)

llrtfstate = RTFllReaderState()
controlspc = False
hexasm = None
dohexasm = False

def hex2bin(hexasm):
    binary = b''
    for i in range(0,len(hexasm) & (~1),2):
        binary += int(hexasm[i:i+2].decode('ascii'),16).to_bytes(1,'little')
    return binary

for ent in RTFllParse(rawrtf,llrtfstate):
    if ent.token == 'text':
        if dohexasm:
            if re.match(b'^[0-9a-fA-F]+$',ent.text):
                hexasm += ent.text
                continue
            else:
                binary = hex2bin(hexasm)
                if len(binary) > 0:
                    sys.stdout.buffer.write(b'\\bin'+str(len(binary)).encode('ascii')+b' ')
                    sys.stdout.buffer.write(binary)
                    controlspc = True
                dohexasm = False
    elif ent.token == 'control' and dohexasm and len(hexasm) == 0:
        True
    else:
        if dohexasm:
            binary = hex2bin(hexasm)
            if len(binary) > 0:
                sys.stdout.buffer.write(b'\\bin'+str(len(binary)).encode('ascii')+b' ')
                sys.stdout.buffer.write(binary)
                controlspc = True
            dohexasm = False
    #
    if ent.token == 'control':
        if ent.destination:
            sys.stdout.buffer.write(b'\\*')
        sys.stdout.buffer.write(b'\\'+ent.text)
        if not ent.param == None:
            sys.stdout.buffer.write(str(ent.param).encode('ascii'))
        controlspc = True
        #
        if ent.text == b'objdata' or ent.text == b'pict':
            dohexasm = True
            hexasm = b''
    elif ent.token == 'binary':
        sys.stdout.buffer.write(b'\\bin'+str(len(ent.binary)).encode('ascii')+b' ')
        controlspc = True
        sys.stdout.buffer.write(ent.binary)
    else:
        if controlspc:
            controlspc = False
            if re.match(b'[a-zA-Z0-9\- ]',ent.text):
                sys.stdout.buffer.write(b' ')
        sys.stdout.buffer.write(ent.text)

