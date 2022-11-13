#!/usr/bin/python3

import os
import re
import csv
import glob
import json
import zlib
import math
import copy
import struct
import pathlib

import apodjson

images = { }

# scan
g = glob.glob("tables/**/image-*",recursive=True)
for path in g:
    pp = pathlib.PurePath(path)
    suffix = pp.suffix.lower()
    if not (suffix == ".jpg" or suffix == ".png" or suffix == ".webp" or suffix == ".gif"):
        continue
    stem = pp.stem
    imgid = stem[6:] # cut off "image-"
    if imgid in images:
        print("Warning: Image already exists id "+imgid+" in "+images[imgid]["path"])
        continue
    images[imgid] = { "id": imgid, "path": path, "suffix": suffix }

# write it
if not os.path.exists("compiled"):
    os.mkdir("compiled")

apodjson.write_json("compiled/images.json",images);

