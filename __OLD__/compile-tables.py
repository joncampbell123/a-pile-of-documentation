#!/usr/bin/python3

import os
import glob
import json
import pathlib

import common_json_help_module
import table_reader_module
import book_reader_module

book_reader_module.load_books()
table_reader_module.load_tables_base()
table_reader_module.load_tables()

try:
    os.mkdir("compiled",mode=0o755)
except:
    True

final_json = { }

final_json["tables"] = { }
for table_id in table_reader_module.tables_by_id.keys():
    table = table_reader_module.tables_by_id[table_id]
    table.expand_source()
    final_json["tables"][table_id] = table.serialize_to_compiled_json()

final_json["sources"] = { }
for book_id in book_reader_module.book_by_id.keys():
    book = book_reader_module.book_by_id[book_id];
    final_json["sources"][book_id] = book.serialize_to_compiled_json()

f = open("compiled/tables.json","w")
json.dump(final_json,f,indent="\t")
f.close()
