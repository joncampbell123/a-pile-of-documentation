#!/usr/bin/python3

import csv

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases
# hexadecimal, decimal, octal, binary
f = open("gen-numbers-bases.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Integer numbers in various common bases',                            '#table-title'])
csw.writerow([])
for i in range(0,1025):
    vhex = hex(i)[2:] # strip off the '0x'
    while len(vhex) < 3:
        vhex = '0' + vhex
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    while len(voct) < 5:
        voct = '0' + voct
    vbin = bin(i)[2:] # strip off the '0b'
    while len(vbin) < 11:
        vbin = '0' + vbin
    #
    csw.writerow([vhex,vdec,voct,vbin])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of powers of 2 in various common bases
# hexadecimal, decimal, octal, binary
f = open("gen-numbers-pow2.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Power',  'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric','numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',  'right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Power of 2 integer numbers in various common bases',                           '#table-title'])
csw.writerow([])
for pi in range(0,63):
    i = 1 << pi
    vhex = hex(i)[2:] # strip off the '0x'
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    vbin = bin(i)[2:] # strip off the '0b'
    #
    csw.writerow([str(pi),vhex,vdec,voct,vbin])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as signed 2's complement 16-bit integers
# hexadecimal, decimal, octal, binary
f = open("gen-numbers-int16-2scmp.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Signed integer value', 'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric',              'numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',                'right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Integer numbers in various common bases as signed 2\'s complement 16-bit integers',          '#table-title'])
csw.writerow([])
for si in range(-256,257):
    if si >= 0:
        i = si
    else:
        i = 0x10000 + si
    #
    vhex = hex(i)[2:] # strip off the '0x'
    while len(vhex) < 4:
        vhex = '0' + vhex
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    while len(voct) < 6:
        voct = '0' + voct
    vbin = bin(i)[2:] # strip off the '0b'
    while len(vbin) < 16:
        vbin = '0' + vbin
    #
    csw.writerow([str(si),vhex,vdec,voct,vbin])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as signed 1's complement 16-bit integers
# hexadecimal, decimal, octal, binary
f = open("gen-numbers-int16-1scmp.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Signed integer value', 'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric',              'numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',                'right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Integer numbers in various common bases as signed 1\'s complement 16-bit integers',          '#table-title'])
csw.writerow([])
for si in range(-257,257):
    if si >= 0:
        i = si
    else:
        i = 0x10000 + si
    #
    vhex = hex(i)[2:] # strip off the '0x'
    while len(vhex) < 4:
        vhex = '0' + vhex
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    while len(voct) < 6:
        voct = '0' + voct
    vbin = bin(i)[2:] # strip off the '0b'
    while len(vbin) < 16:
        vbin = '0' + vbin
    #
    if si >= 0:
        csw.writerow([str(si),vhex,vdec,voct,vbin])
    else:
        csw.writerow(["-"+str(-(si+1)),vhex,vdec,voct,vbin])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as sign-magnitude 16-bit integers
# hexadecimal, decimal, octal, binary
f = open("gen-numbers-int16-sm.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Signed integer value', 'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric',              'numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',                'right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Integer numbers in various common bases as sign-magnitude 16-bit integers',                  '#table-title'])
csw.writerow([])
for si in range(-257,257):
    if si >= 0:
        i = si
    else:
        i = 0x7FFF - si
    #
    vhex = hex(i)[2:] # strip off the '0x'
    while len(vhex) < 4:
        vhex = '0' + vhex
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    while len(voct) < 6:
        voct = '0' + voct
    vbin = bin(i)[2:] # strip off the '0b'
    while len(vbin) < 16:
        vbin = '0' + vbin
    #
    if si >= 0:
        csw.writerow([str(si),vhex,vdec,voct,vbin])
    else:
        csw.writerow(["-"+str(-(si+1)),vhex,vdec,voct,vbin])
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as gray codes
# hexadecimal, decimal, octal, binary

def graycode(i):
    return i ^ (i >> 1)

f = open("gen-numbers-gray-codes.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
csw.writerow(['Original hexadecimal', 'Original decimal', 'Original octal', 'Original binary', 'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric:base=16',      'numeric:base=10',  'numeric:base=8', 'numeric:base=1',  'numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',                'right',            'right',          'right',           'right',          'right',          'right',         'right',         '#column-align'])
csw.writerow(['Integer numbers in various common bases as gray codes',                                                                                               '#table-title'])
csw.writerow([])
pgi = 0
for i in range(0,257):
    gi = graycode(i)
    #
    ovhex = hex(i)[2:] # strip off the '0x'
    while len(ovhex) < 2:
        ovhex = '0' + ovhex
    ovdec = str(i)
    ovoct = oct(i)[2:] # strip off the '0o'
    while len(ovoct) < 3:
        ovoct = '0' + ovoct
    ovbin = bin(i)[2:] # strip off the '0b'
    while len(ovbin) < 9:
        ovbin = '0' + ovbin
    #
    vhex = hex(gi)[2:] # strip off the '0x'
    while len(vhex) < 2:
        vhex = '0' + vhex
    vdec = str(gi)
    voct = oct(gi)[2:] # strip off the '0o'
    while len(voct) < 3:
        voct = '0' + voct
    vbin = bin(gi)[2:] # strip off the '0b'
    while len(vbin) < 9:
        vbin = '0' + vbin
    #
    csw.writerow([ovhex,ovdec,ovoct,ovbin,vhex,vdec,voct,vbin])
    #
    if i > 0:
        bc = gi ^ pgi # make sure only one bit changed
        if not (bc & (bc - 1)) == 0: # if not power of 2
            raise Exception("Gray code encoding for "+str(i)+" failed")
    #
    pgi = gi
f.close()
