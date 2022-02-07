#!/usr/bin/python3

import glob
import json

def load_json(path):
    f = open(path,"r",encoding='utf-8')
    j = json.load(f)
    f.close()
    return j
 
