#!/bin/bash
../../../unicodetbl2csv_sbcs.py --in ../cp850/CP850.TXT --out unicode-consortium--cp858.csv || exit 1
grep -v '^0xd5,' unicode-consortium--cp858.csv >unicode-consortium--cp858.csv.tmp || exit 1
echo '0xd5,"EURO SIGN","€",' >>unicode-consortium--cp858.csv.tmp || exit 1
mv -v unicode-consortium--cp858.csv.tmp unicode-consortium--cp858.csv || exit 1
