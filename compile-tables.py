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
    table = { }
    columns = [ ]
    sources = [ ]
    key_column = None
    table_format_type = None
    def filter_key_value_by_type(self,key):
        if not self.key_column == None:
            type = self.key_column.get("type")
            if type == "uint8_t" or type == "uint16_t" or type == "uint32_t" or type == "uint":
                return int(key,0)
        #
        return key
    def add_info(self,json):
        source_idx = None
        if "source" in json:
            source_idx = len(self.sources)
            self.sources.append(json["source"])
        if "table" in json:
            s_table = json["table"]
            if isinstance(s_table, dict):
                keys = s_table.keys()
                for key in keys:
                    if self.table_format_type == "key=value":
                        table_key = self.filter_key_value_by_type(key)
                        if not table_key in self.table:
                            self.table[table_key] = [ ]
                        if not source_idx == None:
                            s_table[key]["source index"] = source_idx
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

load_tables_base()
load_tables()

