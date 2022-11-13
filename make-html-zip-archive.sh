#!/bin/bash
rm -f compiled/html/download.zip
(cd compiled/html && zip -r -9 ../html-zip.zip * && mv -v ../html-zip.zip download.zip)
