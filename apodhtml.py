
import re

def htmlidfilter(x):
    return re.sub('[^a-zA-Z0-9_\-\.]','_',x)

# ex: <a id="t:source:id:sourceid:part:partid">...<a href="#t:source:id:sourceid:part:partid">duh</a>
def mkhtmlid(idtype,sid,path=None):
    r = "t:"+idtype+":id:"+sid
    if not path == None:
        for pelo in path:
            if "level" in pelo and "name" in pelo:
                r += ":" + htmlidfilter(pelo["level"]) + ":" + htmlidfilter(pelo["name"])
            elif "group index" in pelo:
                r += ":g" + str(pelo["group index"])
    return r

