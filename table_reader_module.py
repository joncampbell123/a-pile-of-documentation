
import os
import glob
import json
import pathlib

import common_json_help_module
import book_reader_module

# dictionary: table id -> table object
tables_by_id = { }

# table object
class Table:
    id = None
    name = None
    base_json = None
    description = None
    notes = None
    table = None
    columns = None
    sources = None
    key_column = None
    table_format_type = None
    def expand_source_book(self,src,bookid):
        if not bookid in book_reader_module.book_by_id:
            raise Exception("No such book "+bookid)
        book = book_reader_module.book_by_id[bookid]
        #
        citation = { }
        if not book.title == None:
            citation["title"] = book.title
        if not book.author == None:
            citation["author"] = book.author
        if not book.publisher == None:
            citation["publisher"] = book.publisher
        if not book.copyright_year == None:
            citation["year"] = book.copyright_year
        if not book.type == None:
            citation["type"] = book.type
        if not book.url == None:
            citation["url"] = book.url
        # Making a source file PER WEBSITE URL is absurd, allow the table to provide the URL
        if "url" in src:
            citation["url"] = src["url"]
            del src["url"]
        #
        src["citation"] = citation
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
        for i in range(valid_len):
            if matchname[i] in src:
                del src[matchname[i]]
            #
            obj = { }
            if not match[i] == None:
                obj["path"] = match[i]
            if not matchname[i] == None:
                obj["type"] = matchname[i]
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
            elif "website" in src:
                self.expand_source_book(src,src["website"])
    def serialize_to_compiled_json(self):
        f = { }
        f["table"] = self.table
        f["sources"] = self.sources
        f["description"] = self.description
        f["notes"] = self.notes
        f["name"] = self.name
        f["columns"] = self.columns
        f["table format type"] = self.table_format_type
        if not self.key_column == None:
            f["key column"] = self.key_column
        return f;
    def filter_key_value_by_type(self,key):
        if not self.key_column == None:
            type = self.key_column.get("type")
            if type[0:4] == "uint":
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
        self.table = { }
        self.notes = [ ]
        self.columns = [ ]
        self.sources = [ ]
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

                # will throw exception if these keys do not exist
                if isinstance(obj["value"],list):
                    self.columns = obj["value"]
                else:
                    self.columns = [ obj["value"] ]
            else:
                raise Exception("Table json unknown table format type "+str(self.table_format_type)+" in "+self.id)

def load_tables_base():
    g = glob.glob("tables/**/*--base.json",recursive=True)
    for path in g:
        json = common_json_help_module.load_json(path)
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
        json = common_json_help_module.load_json(path)
        #
        file_table_id = None
        source_id = None
        file_path = pathlib.Path(path)
        if len(file_path.parts) > 0:
            name = file_path.parts[len(file_path.parts)-1]
            #
            if name[-5:] == ".json":
                name = name[:-5]
            #
            name_parts = name.split("--")
            #
            if len(name_parts) > 0:
                file_table_id = name_parts[0]
            else:
                file_table_id = None
            #
            if len(name_parts) > 1:
                source_id = name_parts[1]
            else:
                source_id = None
        #
        if "base definition" in json:
            if json["base definition"] == True:
                continue
        if "id" in json:
            table_id = json["id"]
        if not table_id == file_table_id:
            raise Exception("Table ID must match base of filename, file="+path+" id="+str(table_id))
        #
        if "source" in json:
            what = None
            src = json["source"]
            if "book" in src:
                what = src["book"]
            elif "website" in src:
                what = src["website"]
            #
            if not what == source_id:
                fp = file_path.parts[0:len(file_path.parts)-1]
                fa = ""
                for f in fp:
                    if not fa == "":
                        fa = fa + "/"
                    fa = fa + f
                print("File name "+path+" is wrong")
                print("Suggest renaming to: "+fa+"/"+str(table_id)+"--"+str(what)+".json")
                raise Exception("Source ID in table must match second segment of filename, file="+path+" table_id="+str(table_id)+" source_id="+str(what)+" filesourceid="+str(source_id))
        #
        if table_id in tables_by_id:
            table = tables_by_id[table_id]
            table.add_info(json)
        else:
            raise Exception("Table json refers to undefined table id "+str(table_id)+" in json file "+path)

