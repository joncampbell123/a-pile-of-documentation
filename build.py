#!/usr/bin/python3

import os;
import subprocess;

topdir = os.getcwd();

todolist = [
    {
        "path": "tables/encodings",
        "run": [ "./gen.py", "--only-changed" ]
    },
    {
        "path": "tables/numbers",
        "run": [ "./gen.py", "--only-changed" ]
    },
    {
        "path": "images/encodings",
        "run": [ "./gen.py", "--only-changed" ]
    }
]

for todo in todolist:
    announce = ""
    if "path" in todo:
        announce += " task in " + todo["path"]
    if "run" in todo:
        announce += " to run " + str(todo["run"])
    if announce == "":
        announce = "task"
    announce = announce.strip()
    #
    print(announce)
    if "path" in todo:
        os.chdir(os.path.join(os.path.abspath(topdir),todo["path"]))
    else:
        os.chdir(topdir)
    #
    if "run" in todo:
        subprocess.run(todo["run"], check=True)

