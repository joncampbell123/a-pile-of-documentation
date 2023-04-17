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

