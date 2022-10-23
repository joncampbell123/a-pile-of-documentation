
# process base descriptions
g = glob.glob("tables/**/*.json",recursive=True)
for path in g:
    pathelem = path.split('/')
    if len(pathelem) < 1:
        raise Exception("What??")
    basename = pathelem[-1] # the last element
    if basename == None or basename == "":
        raise Exception("What??")
    if len(basename) >= 11 and basename[-11:] == "--base.json":
        continue
    #
    ji = load_json(path)
    if not "id" in ji:
        continue
    if "base definition" in ji:
        if ji["base definition"] == True:
            raise Exception("Table "+ji["id"]+" is base definition, but does not have --base.json extension")
    if not ji["id"] in tables:
        raise Exception("Table "+ji["id"]+" does not exist (no base def?)")
    table = tables[ji["id"]]
    # the "id" must match the file name because that's the only way we can keep our sanity
    # maintaining this collection.
    if not basename[0:len(ji["id"])+2] == (ji["id"] + "--"):
        raise Exception("Table "+ji["id"]+" id does not match filename "+basename)
    # our JSON has schema version numbers now, because in the future we may have to make
    # some changes
    if not "schema" in ji:
        raise Exception("Table "+ji["id"]+" has no schema information")
    if not "version" in ji["schema"]:
        raise Exception("Table "+ji["id"]+" has no schema version")
    ver = ji["schema"]["version"]
    if ver < 1 or ver > 1:
        raise Exception("Table "+ji["id"]+" is using unsupported schema "+str(ver))
    # table column name to index lookup
    if not "table columns" in table:
        raise Exception("Table "+ji["id"]+" is missing table columns")
    # source id?
    sourceref = None
    source_id = None
    source_type = None
    if "source" in ji:
        source_obj = ji["source"]
        if "id" in source_obj:
            source_id = source_obj["id"]
        if "type" in source_obj:
            source_type = source_obj["type"]
    # source id must be in file name along with table id. sorry, this is how we maintain sanity.
    if not source_id == None:
        cut = len(ji["id"])+2+len(source_id)
        match = ji["id"] + "--" + source_id
        if len(basename) >= (cut+2) and basename[cut+2:2] == "--":
            match = match + "--"
            cut = cut + 2
        if not basename[0:cut] == match:
            raise Exception("Table "+ji["id"]+" id and source "+source_id+" id does not match filename "+basename)
        # does the source exist?
        if not source_id in sources:
            raise Exception("Table "+ji["id"]+" no such source "+source_id)
        sourceref = sources[source_id]
        if "type" in sourceref and not source_type == None:
            if not sourceref["type"] == source_type:
                raise Exception("Table "+ji["id"]+" source "+source_id+" type mismatch")
    #
    toc = None
    toc_refby = None
    toc_contents = None
    toc_hierlist = None
    if not sourceref == None:
        if "table of contents" in sourceref:
            toc = sourceref["table of contents"]
            if not type(toc) == dict:
                raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents not object")
            if "hierarchy" in toc:
                toc_hierlist = toc["hierarchy"]
                if not type(toc_hierlist) == list:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents hierarchy not array")
            if "contents" in toc:
                toc_contents = toc["contents"]
                if not type(toc_contents) == dict:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents contents not object")
            if "reference by" in toc:
                toc_refby = toc["reference by"]
                if not type(toc_refby) == dict:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" table of contents reference by not object")
    #
    if not source_id == None and not source_obj == None and not sourceref == None:
        if "where" in source_obj:
            where = source_obj["where"]
            if not type(where) == dict:
                raise Exception("Table "+ji["id"]+" source "+source_id+" where not an object")
            lookup = { }
            lookpaths = { }
            for key in where:
                val = where[key]
                if key[0] == '@':
                    lookup[key] = val
            if len(lookup) > 0:
                matches = [ ]
                if toc_contents == None or toc_hierlist == None or toc == None or toc_refby == None:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" where object with no or incomplete table of contents")
                for level in lookup:
                    value = lookup[level]
                    if not value in toc_refby:
                        raise Exception("Table "+ji["id"]+" source "+source_id+" no such "+level+" "+value)
                    robj = toc_refby[value]
                    if type(robj) == dict:
                        robj = [ robj ]
                    for roe in robj:
                        if not "path" in roe:
                            raise Exception("Table "+ji["id"]+" source "+source_id+" no such path for "+level+" "+value)
                        rpath = roe["path"]
                        match = False
                        for pelo in rpath:
                            if "level" in pelo and "name" in pelo:
                                if pelo["level"] in lookup:
                                    if pelo["name"] == lookup[pelo["level"]]:
                                        match = True
                                    else:
                                        match = False
                                        break # from for loop
                        if match == True: # make sure everything the where clause specifies is actually there
                            chk = tocpathtoobj(rpath)
                            for level in lookup:
                                if not level in chk:
                                    match = False
                                    break
                        if match == True: # only add paths where everything matches the where object lookup
                            matches.append(rpath)
                #
                if len(matches) == 0:
                    raise Exception("Table "+ji["id"]+" source "+source_id+" no matches for where clause")
                # the longest path is the authoratative one, match all others against it.
                # to do this, sort longest to shortest.
                # if there is a mismatch and the lookup refers to it, discard the mismatch.
                # if there is a mismatch and the lookup does not refer to it, it's an ambiguity and therefore an error
                if len(matches) > 1:
                    matches.sort(reverse=True,key=sortbylen)
                # first add to where clause
                authoritah = tocpathtoobj(matches[0])
                for level in authoritah:
                    name = authoritah[level]
                    if level in where:
                        if not name == where[level]:
                            print(authoritah)
                            print(where)
                            raise Exception("Whoah, where object mismatch for "+level+"?")
                    else:
                        where[level] = name
                # then go down the array, checking (does nothing if only one match)
                if len(matches) > 1:
                    scan = 1
                    nmatches = [ matches[0] ]
                    while scan < len(matches):
                        pel = tocpathtoobj(matches[scan])
                        match = None
                        for level in lookup:
                            pval = ""
                            if level in pel:
                                pval = pel[level]
                            aval = ""
                            if level in authoritah:
                                aval = authoritah[level]
                            #
                            if pval == aval:
                                match = True
                            else:
                                match = False
                                break
                        #
                        if match == True:
                            print(['match',match])
                            nmatches.append(matches[scan])
                        scan = scan + 1
                    #
                    matches = nmatches
                # if after all the source resolution there are multiple results, then the where clause is ambiguous
                # and more information is needed
                if len(matches) > 1:
                    print(matches)
                    raise Exception("Table "+ji["id"]+" source "+source_id+" where clause is ambigious. More source information needed to select the specific part of the source.")
                #
                where["path"] = matches[0]

