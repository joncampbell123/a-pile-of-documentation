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

def genfrag(bookid,ji):
    r = b"<a id=\""+apodhtml.mkhtmlid("source",ji["id"]).encode('UTF-8')+b"\"></a>"
    r += b"<table>\n"
    if "type" in ji:
        r += b"<tr><td>Type:</td><td>"+apodhtml.htmlescape(ji["type"]).encode('UTF-8')+b"</td>\n";
    if "title" in ji:
        r += b"<tr><td>Title:</td><td>"+apodhtml.htmlescape(ji["title"]).encode('UTF-8')+b"</td>\n";
    if "url" in ji:
        r += b"<tr><td>URL:</td><td><a target=\"_blank\" href=\""+ji["url"].encode('UTF-8')+b"\">"+apodhtml.htmlescape(ji["url"]).encode('UTF-8')+b"</a></td>\n";
    r += b"</table>"
    return r

def writefrag(bookid,ji,htmlfrag):
    path = "compiled/sources/"+bookid+".html.frag"
    f = open(path,"wb")
    f.write(htmlfrag)
    f.close()

def writewhole(bookid,ji,htmlfrag):
    path = "compiled/sources/"+bookid+".html"
    f = open(path,"wb")
    f.write("<!doctype html><html><head>".encode('UTF-8'))
    f.write("<meta charset=\"UTF-8\">".encode('UTF-8'))
    f.write("<meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\">".encode('UTF-8'))
    if "title" in ji:
        f.write(("<title>"+apodhtml.htmlescape(ji["title"])+"</title>").encode('UTF-8'))
    f.write("</head><body>".encode('UTF-8'))
    f.write(htmlfrag)
    f.write("</body></html>".encode('UTF-8'))
    f.close()

# process
g = glob.glob("compiled/sources/*.json",recursive=True)
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
    #
    htmlfrag = genfrag(ji["id"],ji)
    writefrag(ji["id"],ji,htmlfrag)
    writewhole(ji["id"],ji,htmlfrag)
