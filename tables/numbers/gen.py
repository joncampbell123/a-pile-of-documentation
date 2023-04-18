#!/usr/bin/python3

import csv
import math

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
    while len(vhex) < 16:
        vhex = '0' + vhex
    vdec = str(i)
    voct = oct(i)[2:] # strip off the '0o'
    while len(voct) < 21:
        voct = '0' + voct
    vbin = bin(i)[2:] # strip off the '0b'
    while len(vbin) < 64:
        vbin = '0' + vbin
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
csw.writerow(['Original hexadecimal', 'Original decimal', 'Original octal', 'Original binary', '-',         'Hexadecimal',    'Decimal',        'Octal',         'Binary',        '#column-names'])
csw.writerow(['numeric:base=16',      'numeric:base=10',  'numeric:base=8', 'numeric:base=1',  'separator', 'numeric:base=16','numeric:base=10','numeric:base=8','numeric:base=2','#column-format'])
csw.writerow(['right',                'right',            'right',          'right',           '',          'right',          'right',          'right',         'right',         '#column-align'])
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
    csw.writerow([ovhex,ovdec,ovoct,ovbin,'-',vhex,vdec,voct,vbin])
    #
    if i > 0:
        bc = gi ^ pgi # make sure only one bit changed
        if not (bc & (bc - 1)) == 0: # if not power of 2
            raise Exception("Gray code encoding for "+str(i)+" failed")
    #
    pgi = gi
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as gray codes
# hexadecimal, decimal, octal, binary
def write_logic2_table(csvname,title,lambdafunc):
    f = open(csvname,mode="w",encoding="utf-8",newline="")
    csw = csv.writer(f)
    csw.writerow(['Input 1 (P)',   'Input 2 (Q)',   'Output',        '#column-names'])
    csw.writerow(['numeric:base=1','numeric:base=1','numeric:base=1','#column-format'])
    csw.writerow(['right',         'right',         'right',         '#column-align'])
    csw.writerow([title,                                             '#table-title'])
    csw.writerow([])
    for i in range(0,4):
        i1 = (i >> 1) & 1
        i2 = (i >> 0) & 1
        ou = lambdafunc(i1,i2)
        csw.writerow([str(i1),str(i2),str(ou)])
    f.close()

write_logic2_table("gen-logic-nor.csv","Not OR (NOR)",lambda i1,i2: 1 ^ (i1 | i2))
write_logic2_table("gen-logic-xor.csv","eXclusive OR (XOR)",lambda i1,i2: (i1 ^ i2))
write_logic2_table("gen-logic-nand.csv","Not AND (NAND)",lambda i1,i2: 1 ^ (i1 & i2))
write_logic2_table("gen-logic-and.csv","AND",lambda i1,i2: (i1 & i2))
write_logic2_table("gen-logic-xnor.csv","eXclusive NOR (XNOR)",lambda i1,i2: 1 ^ (i1 ^ i2))
write_logic2_table("gen-logic-or.csv","OR",lambda i1,i2: (i1 | i2))

#--------------------------------------------------------------------------------------------------------
# list of numbers in various common bases as encoding of 16-bit IEEE floating point
# float, sign, exponent, mantissa, hexadecimal, binary
def common_float_csv_header(csw,float_bits):
    csw.writerow(['Float value', 'Sign',           'Exponent',      'Mantissa',       'Hexadecimal',    'Binary',        'Notes',  '#column-names'])
    csw.writerow(['numeric',     'numeric',        'numeric',       'numeric:base=16','numeric:base=16','numeric:base=2','string', '#column-format'])
    csw.writerow(['right',       'right',          'right',         'right',          'right',          'right',         'left',   '#column-align'])
    csw.writerow([str(float_bits)+'-bit IEEE floating point numbers and their encodings as various binary encodings',              '#table-title'])
    csw.writerow(['Final float value, without sign, is mantissa * pow(2.0,exponent)',                                              '#table-note'])
def common_float_csv_gen(csw,float_bits,mant_bits,exp_bits,exp_bias,explicit_mantissa_msb=False):
    float_hex_digits = int((float_bits + 3) / 4)
    #
    if explicit_mantissa_msb == True:
        exp_shift = mant_bits + 1
    else:
        exp_shift = mant_bits
    #
    mant_implicit = 1 << mant_bits
    exp_mask = (1 << exp_bits) - 1
    exp_min = -exp_bias
    exp_max = exp_mask + exp_min - 1
    # Python seems to do only double precision float, limit the exponent range or else the 80-bit Intel format will cause a fault
    real_exp_min = exp_min
    real_exp_max = exp_max
    if exp_min < -1023:
        exp_min = -1023
    if exp_max > 1023:
        exp_max = 1023
    #
    for sgn in range(0,2):
        ssgn = ['','-'][sgn]
        for rexp in range(exp_min,exp_max + 1):
            for rmant in [0,1<<(mant_bits-2),2<<(mant_bits-2),3<<(mant_bits-2)]:
                if rexp > real_exp_min:
                    note = ""
                    mant = rmant | mant_implicit # normal
                    exp = rexp
                else:
                    note = "Subnormal float, implicit bit 0"
                    mant = rmant # subnormal
                    exp = exp_min + 1
                #
                fval = mant * math.pow(2, exp - mant_bits)
                encoding = (sgn << (float_bits-1)) | (((rexp + exp_bias) & exp_mask) << exp_shift) | rmant
                if explicit_mantissa_msb == True:
                    encoding = encoding | mant_implicit
                #
                vhex = hex(encoding)[2:] # strip off the '0x'
                while len(vhex) < float_hex_digits:
                    vhex = '0' + vhex
                vbin = bin(encoding)[2:] # strip off the '0b'
                while len(vbin) < float_bits:
                    vbin = '0' + vbin
                #
                csw.writerow([ssgn+str(fval),str(sgn),str(exp),hex(mant),vhex,vbin,note])
    # gotta mention infinity and Nan for reference, too
    for sgn in range(0,2):
        rexp = exp_mask - exp_bias
        rmant = 0
        ssgn = ['','-'][sgn]
        note = "Infinity"
        encoding = (sgn << (float_bits-1)) | (((rexp + exp_bias) & exp_mask) << exp_shift) | rmant
        if explicit_mantissa_msb == True:
            encoding = encoding | mant_implicit
        #
        vhex = hex(encoding)[2:] # strip off the '0x'
        while len(vhex) < float_hex_digits:
            vhex = '0' + vhex
        vbin = bin(encoding)[2:] # strip off the '0b'
        while len(vbin) < float_bits:
            vbin = '0' + vbin
        #
        csw.writerow([ssgn+"∞",str(sgn),str(rexp),hex(rmant),vhex,vbin,note])
    for sgn in range(0,2):
        rexp = exp_mask - exp_bias
        rmant = 1
        ssgn = ['','-'][sgn]
        note = "Quiet Not A Number"
        encoding = (sgn << (float_bits-1)) | (((rexp + exp_bias) & exp_mask) << exp_shift) | rmant
        if explicit_mantissa_msb == True:
            encoding = encoding | mant_implicit | (mant_implicit >> 1)
        #
        vhex = hex(encoding)[2:] # strip off the '0x'
        while len(vhex) < float_hex_digits:
            vhex = '0' + vhex
        vbin = bin(encoding)[2:] # strip off the '0b'
        while len(vbin) < float_bits:
            vbin = '0' + vbin
        #
        csw.writerow([ssgn+"Nan",str(sgn),str(rexp),hex(rmant),vhex,vbin,note])
    for sgn in range(0,2):
        rexp = exp_mask - exp_bias
        rmant = mant_implicit >> 1
        ssgn = ['','-'][sgn]
        note = "Signalling Not A Number"
        encoding = (sgn << (float_bits-1)) | (((rexp + exp_bias) & exp_mask) << exp_shift) | rmant
        if explicit_mantissa_msb == True:
            encoding = encoding | mant_implicit
        #
        vhex = hex(encoding)[2:] # strip off the '0x'
        while len(vhex) < float_hex_digits:
            vhex = '0' + vhex
        vbin = bin(encoding)[2:] # strip off the '0b'
        while len(vbin) < float_bits:
            vbin = '0' + vbin
        #
        csw.writerow([ssgn+"sNan",str(sgn),str(rexp),hex(rmant),vhex,vbin,note])

f = open("gen-numbers-ieeefloat16.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
common_float_csv_header(csw,float_bits=16)
csw.writerow(['Mantissa shown with implicit bit that is not stored in the final encoding',                                     '#table-note'])
csw.writerow([])
common_float_csv_gen(csw,float_bits=16,mant_bits=10,exp_bits=5,exp_bias=15) # seee'eeff'ffff'ffff 16 bits
f.close()

f = open("gen-numbers-ieeefloat32.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
common_float_csv_header(csw,float_bits=32)
csw.writerow(['Mantissa shown with implicit bit that is not stored in the final encoding',                                     '#table-note'])
csw.writerow([])
common_float_csv_gen(csw,float_bits=32,mant_bits=23,exp_bits=8,exp_bias=127) # seee'eeee'efff'ffff'ffff'ffff'ffff'ffff 32 bits
f.close()

f = open("gen-numbers-ieeefloat64.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
common_float_csv_header(csw,float_bits=64)
csw.writerow(['Mantissa shown with implicit bit that is not stored in the final encoding',                                     '#table-note'])
csw.writerow([])
common_float_csv_gen(csw,float_bits=64,mant_bits=52,exp_bits=11,exp_bias=1023)
f.close()

f = open("gen-numbers-ieeefloat80.csv",mode="w",encoding="utf-8",newline="")
csw = csv.writer(f)
common_float_csv_header(csw,float_bits=80)
csw.writerow(['Mantissa shown with implicit bit that is always stored in the final encoding',                                  '#table-note'])
csw.writerow([])
common_float_csv_gen(csw,float_bits=80,mant_bits=63,exp_bits=15,exp_bias=16383,explicit_mantissa_msb=True)
f.close()

#--------------------------------------------------------------------------------------------------------
# list of numbers and logical operators
# hexadecimal, decimal, octal, binary
def write_logichex_table(csvname,title,lambdafunc):
    f = open(csvname,mode="w",encoding="utf-8",newline="")
    csw = csv.writer(f)
    csw.writerow(['Input 1 (P) (bin)','Input 1 (P) (hex)','Input 2 (Q) (bin)','Input 2 (Q) (hex)','Output (bin)',  'Output (hex)',   '#column-names'])
    csw.writerow(['numeric:base=1',   'numeric:base=16',  'numeric:base=1',   'numeric:base=16',  'numeric:base=1','numeric:base=16','#column-format'])
    csw.writerow(['right',            'right',            'right',            'right',            'right',         'right',          '#column-align'])
    csw.writerow([title,                                                                                                             '#table-title'])
    csw.writerow([])
    for i in range(0,256):
        i1 = (i >> 4) & 0xF
        i2 = (i >> 0) & 0xF
        ou = lambdafunc(i1,i2)
        i1h = hex(i1)[2:]
        while len(i1h) < 2:
            i1h = '0' + i1h
        i1b = bin(i1)[2:]
        while len(i1b) < 4:
            i1b = '0' + i1b
        i2h = hex(i2)[2:]
        while len(i2h) < 2:
            i2h = '0' + i2h
        i2b = bin(i2)[2:]
        while len(i2b) < 4:
            i2b = '0' + i2b
        ouh = hex(ou)[2:]
        while len(ouh) < 2:
            ouh = '0' + ouh
        oub = bin(ou)[2:]
        while len(oub) < 4:
            oub = '0' + oub
        csw.writerow([i1b,i1h,i2b,i2h,oub,ouh])
    f.close()

write_logichex_table("gen-logichex-nor.csv","Not OR (NOR)",lambda i1,i2: 0xF ^ (i1 | i2))
write_logichex_table("gen-logichex-xor.csv","eXclusive OR (XOR)",lambda i1,i2: (i1 ^ i2))
write_logichex_table("gen-logichex-nand.csv","Not AND (NAND)",lambda i1,i2: 0xF ^ (i1 & i2))
write_logichex_table("gen-logichex-and.csv","AND",lambda i1,i2: (i1 & i2))
write_logichex_table("gen-logichex-xnor.csv","eXclusive NOR (XNOR)",lambda i1,i2: 0xF ^ (i1 ^ i2))
write_logichex_table("gen-logichex-or.csv","OR",lambda i1,i2: (i1 | i2))

