#!/usr/bin/python3

import os
import glob
import json
import pathlib

# dictionary: table id -> table object
tables_by_id = { }

# dictionary: book id -> book object (TODO: Common library module in this project)
book_by_id = { }

# book object
class Book:
    id = None
    type = None
    title = None
    author = None
    publisher = None
    copyright_year = None
    copyright_by = None
    hierarchy = [ ]
    hierarchy_root = None
    hierarchy_search = { }
    base_json = None
    def serialize_to_compiled_json(self):
        f = { }
        f["type"] = book.type
        f["title"] = book.title
        f["author"] = book.author
        f["publisher"] = book.publisher
        f["copyright"] = { }
        f["copyright"]["year"] = book.copyright_year
        f["copyright"]["by"] = book.copyright_by
        f["hierarchy"] = book.hierarchy
        f["hierarchy search"] = book.hierarchy_search
        return f;
    def add_sectionobj(self,obj,json):
        if not json == None:
            if isinstance(json, dict):
                for name in json.keys():
                    if not name in obj:
                        obj[name] = [ ]
                    obj[name].append(json[name])

    def __init__(self,json,file_path):
        self.base_json = json
        file_path = pathlib.Path(file_path)
        if len(file_path.parts) > 0:
            self.id = file_path.parts[len(file_path.parts)-1]
            if self.id[-5:] == ".json":
                self.id = self.id[:-5]
        if self.id == None:
            raise Exception("Book with unknown id given path "+str(file_path))
        self.type = json.get("type")
        self.title = json.get("title")
        self.author = json.get("author")
        self.publisher = json.get("publisher")
        if "copyright" in json:
            obj = json["copyright"]
            self.copyright_year = obj.get("year")
            self.copyright_by = obj.get("by")
        #
        if "hierarchy" in json:
            if isinstance(json["hierarchy"], list):
                self.hierarchy = json["hierarchy"]
                if len(self.hierarchy) > 0:
                    self.hierarchy_root = json[self.hierarchy[0]] # blow up if it does not exist
                    search = [ self.hierarchy_root ]
                    newsearch = None
                    prev_what = None
                    for what in self.hierarchy:
                        if what in self.hierarchy_search:
                            raise Exception("Hierarchy name specified more than once: "+what)
                        self.hierarchy_search[what] = [ ]
                        #
                        if not newsearch == None:
                            for i in range(len(newsearch)):
                                hobj = newsearch[i]
                                if isinstance(hobj, dict):
                                    if what in hobj:
                                        parent_name = hobj["name lookup"]
                                        newsearch[i] = hobj[what]
                                        del hobj[what]
                                        for hobjname in newsearch[i]:
                                            newsearch[i][hobjname]["parent lookup"] = { "name": parent_name, "type": prev_what }
                                        continue
                                #
                                newsearch[i] = { }
                            #
                            search = newsearch
                        #
                        newsearch = [ ]
                        for searchobj in search:
                            for hobjname in searchobj:
                                hobj = searchobj[hobjname]
                                hobj["name lookup"] = hobjname
                                self.hierarchy_search[what].append(hobj)
                                newsearch.append(hobj)
                        #
                        prev_what = what

# table object
class Table:
    id = None
    name = None
    base_json = None
    description = None
    notes = [ ]
    table = { }
    columns = [ ]
    sources = [ ]
    key_column = None
    table_format_type = None
    def expand_source_book(self,src,bookid):
        global book_by_id
        if not bookid in book_by_id:
            raise Exception("No such book "+bookid)
        book = book_by_id[bookid]
        #
        searchobj = None
        hierarchy_key = None
        match = [ ]
        matches = 0;
        matchname = [ ]
        matchnamep = [ ]
        matchobj = [ ]
        for h in book.hierarchy:
            # plural to singular. The book says "parts", "sections", the reference says "part", "section"
            k = h
            if k[-1:] == 's':
                k = k[:-1]
            # match
            m = None
            if k in src:
                matches = matches + 1
                m = src[k]
            match.append(m);
            matchname.append(k)
            matchnamep.append(h)
            matchobj.append(None)
        if matches == 0:
            return
        # fill in the gaps by searching upward
        i = len(match) - 1
        valid_len = None
        while i >= 0:
            if match[i] == None:
                i = i - 1
                continue
            #
            if valid_len == None:
                valid_len = i + 1
            # look up the parent this came from
            search = book.hierarchy_search.get(matchnamep[i])
            if search == None:
                raise Exception("Book hiearchy missing search map for "+matchnamep[i])
            #
            obj = None
            for tobj in search:
                if tobj["name lookup"] == match[i]:
                    obj = tobj;
                    break
            if obj == None:
                raise Exception("No such "+matchname[i]+" named "+match[i])
            matchobj[i] = obj
            if i < 1:
                break
            pobj = obj.get("parent lookup")
            if pobj == None:
                raise Exception("No parent for "+matchname[i]+" named "+match[i])
            if not pobj["type"] in book.hierarchy_search:
                raise Exception("Book hiearchy missing search map for "+pobj["type"])
            i = i - 1
            if not pobj["type"] == matchnamep[i]:
                raise Exception("Wrong parent type. Wanted "+pobj["type"]+" got "+matchnamep[i])
            if not match[i] == None:
                if not pobj["name"] == match[i]:
                    raise Exception("Wrong parent name. Wanted "+pobj["name"]+" got "+match[i])
            else:
                match[i] = pobj["name"]
        #
        if valid_len == None:
            valid_len = 0
        while len(match) > valid_len:
            match.pop()
        while len(matchname) > valid_len:
            matchname.pop()
        while len(matchnamep) > valid_len:
            matchnamep.pop()
        #
        src["where"] = [ ]
        src["where order"] = matchname;
        for i in range(valid_len):
            if matchname[i] in src:
                del src[matchname[i]]
            #
            obj = { }
            if not match[i] == None:
                obj["path"] = match[i]
            if not matchobj[i] == None:
                if isinstance(matchobj[i],dict):
                    if "title" in matchobj[i]:
                        obj["title"] = matchobj[i]["title"]
                    if "page" in matchobj[i]:
                        obj["page"] = matchobj[i]["page"]
            src["where"].append(obj)
    def expand_source(self):
        for src in self.sources:
            if "book" in src:
                self.expand_source_book(src,src["book"])
    def serialize_to_compiled_json(self):
        f = { }
        f["table"] = table.table
        f["sources"] = table.sources
        f["description"] = table.description
        f["notes"] = table.notes
        f["name"] = table.name
        f["columns"] = table.columns
        f["table format type"] = table.table_format_type
        if not table.key_column == None:
            f["key column"] = table.key_column
        return f;
    def filter_key_value_by_type(self,key):
        if not self.key_column == None:
            type = self.key_column.get("type")
            if type == "uint8_t" or type == "uint16_t" or type == "uint32_t" or type == "uint":
                return hex(int(key,0))
        #
        return key
    def add_info(self,json):
        source_idx = None
        if "source" in json:
            source_idx = len(self.sources)
            json["source"]["source index"] = source_idx
            self.sources.append(json["source"])
        if "table" in json:
            s_table = json["table"]
            if isinstance(s_table, dict):
                keys = s_table.keys()
                for key in keys:
                    if self.table_format_type == "key=value":
                        key_str = key
                        table_key = self.filter_key_value_by_type(key)
                        if not table_key in self.table:
                            self.table[table_key] = [ ]
                        if not source_idx == None:
                            s_table[key]["source index"] = source_idx
                        s_table[key]["original key"] = key_str
                        self.table[table_key].append(s_table[key])
    def __init__(self,json):
        self.base_json = json
        if "id" in json:
            self.id = json["id"]
        if "table" in json:
            self.name = json["table"]
        if "description" in json:
            self.description = json["description"]
        if "notes" in json:
            if isinstance(json["notes"], str):
                self.notes.append(json["notes"])
            elif isinstance(json["notes"], list):
                self.notes.extend(json["notes"])
            else:
                raise Exception("Notes element is neither string nor array in "+self.id)
        #
        ok = False
        if "base definition" in json:
            if json["base definition"] == True:
                ok = True
        if not ok == True:
            raise Exception("Table json is not base definition in "+self.id)
        #--NTS: We'll support non-combineable later
        ok = False
        if "combinable" in json:
            if json["combinable"] == True:
                ok = True
        if not ok == True:
            raise Exception("Table json is not combinable in "+self.id)
        #
        if "table format" in json:
            obj = json["table format"]
            self.table_format_type = obj.get("type")
            if self.table_format_type == "key=value":
                self.key_column = obj["key"] # will throw exception if these keys do not exist
                self.columns = [ obj["value"] ] # will throw exception if these keys do not exist
            else:
                raise Exception("Table json unknown table format type "+str(self.table_format_type)+" in "+self.id)

def load_json(path):
    f = open(path,"r",encoding='utf-8')
    j = json.load(f)
    f.close()
    return j

def load_tables_base():
    g = glob.glob("tables/**/*--base.json",recursive=True)
    for path in g:
        json = load_json(path)
        if "table" in json:
            table = Table(json)
            if not table.id == None:
                if table.id in tables_by_id:
                    raise Exception("Table "+table.id+" already defined")
                tables_by_id[table.id] = table

def load_tables():
    g = glob.glob("tables/**/*.json",recursive=True)
    for path in g:
        table_id = None
        json = load_json(path)
        if "base definition" in json:
            if json["base definition"] == True:
                continue
        if "id" in json:
            table_id = json["id"]
        #
        if table_id in tables_by_id:
            table = tables_by_id[table_id]
            table.add_info(json)
        else:
            raise Exception("Table json refers to undefined table id "+str(table_id)+" in json file "+path)

def load_books():
    g = glob.glob("sources/*.json",recursive=True)
    for path in g:
        json = load_json(path)
        book = Book(json,path)
        if not book.id == None:
            if book.id in book_by_id:
                raise Exception("Book "+book.id+" already defined")
            book_by_id[book.id] = book

load_books()
load_tables_base()
load_tables()

try:
    os.mkdir("compiled",mode=0o755)
except:
    True

final_json = { }

final_json["tables"] = { }
for table_id in tables_by_id.keys():
    table = tables_by_id[table_id]
    table.expand_source()
    final_json["tables"][table_id] = table.serialize_to_compiled_json()

final_json["sources"] = { }
for book_id in book_by_id.keys():
    book = book_by_id[book_id];
    final_json["sources"][book_id] = book.serialize_to_compiled_json()

f = open("compiled/tables.json","w")
json.dump(final_json,f,indent="\t")
f.close()
