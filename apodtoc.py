
# contents = the source object, within which the "table of contents" -> "contents" objects
def apodsourcetocpathlookup(source,tocpath):
    if not "table of contents" in source:
        return None
    toc = source["table of contents"]
    if not "contents" in toc:
        return None
    contents = toc["contents"]
    so = contents
    for tocpi in tocpath:
        if "level" in tocpi and "name" in tocpi:
            level = tocpi["level"]
            name = tocpi["name"]
            if not level in so:
                return None
            so = so[level]
            if not name in so:
                return None
            so = so[name]
        elif "group index" in tocpi and "group title" in tocpi:
            gi = tocpi["group index"]
            gt = tocpi["group title"]
            if not "group" in so:
                return None
            so = so["group"]
            if not type(so) == list:
                return None
            if gi >= len(so):
                return None
            so = so[gi]
            if not "title" in so:
                return None
            if not so["title"] == gt:
                return None
        else:
            return None
    #
    return so

