
def htmlidfilter(x):
    return re.sub('[^a-zA-Z0-9_\-\.]','_',x)

# ex: <a id="id:source:part:part">...<a href="#id_source:part:part">duh</a>
def mkhtmlid(sid,path=None):
    r = "id:"+sid
    if not path == None:
        for pelo in path:
            if "level" in pelo and "name" in pelo:
                r += ":" + htmlidfilter(pelo["level"]) + ":" + htmlidfilter(pelo["name"])
    return r

