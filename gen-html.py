#!/usr/bin/python3

import os
import re
import glob
import json
import zlib
import math
import copy
import struct
import pathlib

import apodtoc
import apodjson
import apodhtml

# process
g = glob.glob("compiled/sources/**/*.json",recursive=True)
for path in g:
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    #
    ji = apodjson.load_json(path)
    if not "id" in ji:
        continue
    if not "type" in ji:
        continue
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename == (ji["id"] + ".json"):
        raise Exception("Book "+ji["id"]+" id does not match filename "+basename)

