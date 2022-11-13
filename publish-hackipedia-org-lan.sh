#!/bin/bash
# Jon: For use only on your local LAN. Make sure your SSH public/private keys are set up!
scp -p compiled/html/download.zip jmcdocs@nas.jmc:/mnt/main/jmc-storage/docs/raw/Collections/.apod-update.zip || exit 1
ssh jmcdocs@nas.jmc "(cd /mnt/main/jmc-storage/docs/raw/Collections && ./.apod-update.sh)" || exit 1
ssh jmcdocs@nas.jmc "rm -f /mnt/main/jmc-storage/docs/raw/Collections/.apod-update.zip" || exit 1

