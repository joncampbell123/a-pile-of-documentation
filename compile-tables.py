#!/usr/bin/python3

import glob
import json

# dictionary: table id -> table object
tables_by_id = { }

# table object
class Table:
    id = None
    name = None
    base_json = None
    description = None
    notes = [ ]
    columns = [ ]
    table_format_type = None
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
                self.columns = [ obj["key"], obj["value"] ] # will throw exception if these keys do not exist
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

load_tables_base()

