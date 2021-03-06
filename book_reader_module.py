
import os
import glob
import json
import pathlib

import common_json_help_module

# dictionary: book id -> book object
book_by_id = { }

# book object
class Book:
    id = None
    url = None
    type = None
    title = None
    author = None
    publisher = None
    copyright_year = None
    copyright_by = None
    hierarchy = [ ]
    hierarchy_root = None
    hierarchy_search = None
    base_json = None
    def serialize_to_compiled_json(self):
        f = { }
        if not self.url == None:
            f["url"] = self.url
        if not self.type == None:
            f["type"] = self.type
        if not self.title == None:
            f["title"] = self.title
        if not self.author == None:
            f["author"] = self.author
        if not self.publisher == None:
            f["publisher"] = self.publisher

        f["copyright"] = { }
        if not self.copyright_year == None:
            f["copyright"]["year"] = self.copyright_year
        if not self.copyright_by == None:
            f["copyright"]["by"] = self.copyright_by
        if not f["copyright"]:
            del f["copyright"]

        if not self.hierarchy == None:
            if len(self.hierarchy) > 0:
                f["hierarchy"] = self.hierarchy
        if not self.hierarchy_search == None:
            if self.hierarchy_search:
                f["hierarchy search"] = self.hierarchy_search

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
        if not self.id == json.get("id"):
            raise Exception("Book id does not match file "+str(file_path))
        self.url = json.get("url")
        self.type = json.get("type")
        self.title = json.get("title")
        self.author = json.get("author")
        self.publisher = json.get("publisher")
        if "copyright" in json:
            obj = json["copyright"]
            self.copyright_year = obj.get("year")
            self.copyright_by = obj.get("by")
        #
        self.hierarchy_search = { } # FIXME: Why does initializing as { } in the class fail to reinit, but assiging here makes it work?
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

def load_books():
    g = glob.glob("sources/*.json",recursive=True)
    for path in g:
        json = common_json_help_module.load_json(path)
        book = Book(json,path)
        if not book.id == None:
            if book.id in book_by_id:
                raise Exception("Book "+book.id+" already defined")
            book_by_id[book.id] = book

