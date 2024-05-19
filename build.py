#!/usr/bin/python3

import os;
import subprocess;

topdir = os.getcwd();

# encoding .csv
os.chdir(os.path.join(os.path.abspath(topdir),'tables','encodings'));
print(os.getcwd());
subprocess.run(["./gen.py","--only-changed"], check=True);

# number .csv
os.chdir(os.path.join(os.path.abspath(topdir),'tables','numbers'));
print(os.getcwd());
subprocess.run(["./gen.py","--only-changed"], check=True);

# images, encodings .csv
os.chdir(os.path.join(os.path.abspath(topdir),'images','encodings'));
print(os.getcwd());
subprocess.run(["./gen.py","--only-changed"], check=True);

