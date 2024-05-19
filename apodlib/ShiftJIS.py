
def IsWordSJIS(cc):
    if (cc >= 0x8100 and cc <= 0x9F00) or (cc >= 0xE000 and cc <= 0xEF00):
        b = cc & 0xFF
        if b >= 0x40 and not b == 0x7F:
            return True
    return False

def DecodeSJIS(h,l):
    if h >= 0x81 and h <= 0x9F:
        b1 = (h - 112) * 2
    elif h >= 0xE0 and h <= 0xEF:
        b1 = (h - 176) * 2
    else:
        return [-1,-1]

    if l >= 0x9F:
        b2 = l - 126
    elif l == 0x7F:
        return [-1,-1]
    elif l >= 0x40:
        b1 -= 1
        b2 = l - 31
        if l >= 0x80:
            b2 -= 1
    else:
        b2 = -1

    return [b1,b2]

