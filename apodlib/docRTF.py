
import os
import re
import sys

class RTFllReaderState:
    dummy = None

class RTFToken:
    destination = None
    binary = None # \bin data
    token = None
    param = None
    text = None
    def __init__(self,what=None):
        True
    def __str__(self):
        r = '['+type(self).__name__
        if not self.destination == None:
            r += ' dest='+str(self.destination)
        if not self.binary == None:
            r += ' binary='+str(self.binary)
        if not self.token == None:
            r += ' token='+str(self.token)
        if not self.param == None:
            r += ' param='+str(self.param)
        if not self.text == None:
            r += ' text='+str(self.text)
        r += ']'
        return r

def rawrtfloadfile(path):
    f = open(path,"rb")
    raw = f.read()
    f.close()
    return raw

def RTFllParse(blob,state=RTFllReaderState()):
    i = 0
    while i < len(blob):
        p = re.search(b'\\\\(\\*\\\\)?([a-zA-Z]+)(\-?[0-9]*)? ?|\\\\\'([0-9a-fA-F]{2})|\\\\([^a-zA-Z0-9 ])|(\{|\})|(\r\n|\n\r|[\r\n\f])',blob[i:])
        # group             0         1          2                    3                    4                      5       6
        if p:
            begin = p.span()[0]+i
            end = p.span()[1]+i
            what = blob[begin:end]
            # possible groups
            # 012
            #    3
            #     4
            #      5
            #       6
            groups = p.groups()
            desttag = groups[0]
            ctlaz = groups[1]
            ctlN = groups[2]
            hexen = groups[3]
            ctlesc = groups[4]
            curbr = groups[5]
            nl = groups[6]
            #
            if i < begin:
                t = RTFToken()
                t.token = 'text'
                t.text = blob[i:begin]
                yield t
            #
            if not nl == None:
                True # ignore whitespace
            elif not curbr == None:
                t = RTFToken()
                t.text = curbr
                t.token = curbr.decode('ascii')
                yield t
            elif not ctlesc == None:
                if ctlesc == b'\\' or ctlesc == b'{' or ctlesc == b'}':
                    t = RTFToken()
                    t.token = 'text'
                    t.text = ctlesc.decode('ascii')
                    yield t
                else:
                    t = RTFToken()
                    t.token = 'special'
                    t.text = ctlesc.decode('ascii')
                    yield t
            elif not hexen == None:
                t = RTFToken()
                t.token = 'text'
                t.text = int(hexen.decode('ascii'),16).to_bytes(1,'little')
                yield t
            elif not ctlaz == None:
                t = RTFToken()
                t.token = 'control'
                if not ctlN == None and not ctlN == b'':
                    t.param = int(ctlN.decode('ascii'))
                t.text = ctlaz
                if not desttag == None and not desttag == '':
                    t.destination = True
                #
                # Special handling: \binN N bytes of binary data follow
                if t.text == b'bin':
                    if t.param > 0:
                        i = end
                        end = i + t.param
                        if end > len(blob):
                            end = len(blob)
                        t = RTFToken()
                        t.token = 'binary'
                        t.binary = blob[i:end]
                        yield t
                else:
                    yield t
            else:
                raise Exception("Unexpected! "+str([desttag,ctlaz,ctlN,ctlesc,curbr,hexen,nl]))
            #
            i = end
        else:
            t = RTFToken()
            t.token = 'text'
            t.text = blob[i:]
            yield t
            break

