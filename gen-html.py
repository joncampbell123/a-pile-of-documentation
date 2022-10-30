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
    r += b"<table class=\"apodsource\">\n"
    r += b"<tr class=\"apodsourceid\"><td>ID:</td><td>"+apodhtml.htmlescape(bookid).encode('UTF-8')+b"</td>\n";
    if "type" in ji:
        r += b"<tr class=\"apodsourcetype\"><td>Type:</td><td>"+apodhtml.htmlescape(ji["type"]).encode('UTF-8')+b"</td>\n";
    if "title" in ji:
        r += b"<tr class=\"apodsourcetitle\"><td>Title:</td><td>"+apodhtml.htmlescape(ji["title"]).encode('UTF-8')+b"</td>\n";
    if "url" in ji:
        r += b"<tr class=\"apodsourceurl\"><td>URL:</td><td><a target=\"_blank\" href=\""+ji["url"].encode('UTF-8')+b"\">"+apodhtml.htmlescape(ji["url"]).encode('UTF-8')+b"</a></td>\n";
    if "author" in ji:
        r += b"<tr class=\"apodsourceauthor\"><td>Author:</td><td>"+apodhtml.htmlescape(ji["author"]).encode('UTF-8')+b"</td>\n";
    if "publisher" in ji:
        r += b"<tr class=\"apodsourcepublisher\"><td>Publisher:</td><td>"+apodhtml.htmlescape(ji["publisher"]).encode('UTF-8')+b"</td>\n";
    if "language" in ji:
        r += b"<tr class=\"apodsourcelanguage\"><td>Language:</td><td>"+apodhtml.htmlescape(ji["language"]).encode('UTF-8')+b"</td>\n";
    if "copyright" in ji:
        cpy = ji["copyright"]
        # TODO: Perhaps this can be a list (array) for multiple copyrights
        # TODO: Perhaps "year" can be a list (array) for multiple copyright years
        r += b"<tr class=\"apodsourcecopyright\"><td>Copyright:</td><td>&copy;";
        if "year" in cpy:
            r += b" "+str(cpy["year"]).encode('UTF-8');
        if "by" in cpy:
            r += b" "+cpy["by"].encode('UTF-8');
        r += b"</td>\n";
    if "isbn" in ji:
        isbn = ji["isbn"]
        for what in isbn:
            r += b"<tr class=\"apodsourceisbn\"><td>ISBN:</td><td>"+apodhtml.htmlescape(isbn[what]+" ("+what.upper()+")").encode('UTF-8')+b"</td>\n";
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

