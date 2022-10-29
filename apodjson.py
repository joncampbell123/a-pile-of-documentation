
import os
import re
import glob
import json
import zlib
import math
import copy
import struct
import pathlib

def load_json(path):
    f = open(path,"r",encoding='utf-8')
    j = json.load(f)
    f.close()
    return j

def write_json(path,ji):
    f = open(path,"w",encoding='utf-8')
    json.dump(ji,f,indent=4)
    f.close()


