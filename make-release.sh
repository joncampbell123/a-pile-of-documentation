#!/bin/bash
./rebuild-all || exit 1
./make-html-zip-archive.sh || exit 

