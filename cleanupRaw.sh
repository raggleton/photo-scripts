#!/bin/bash -e
#
# Given a directory, find all RAW files without matching JPG, and delete them

for f in "$1"/*.ARW;
do
    # echo $f
    jpgname=${f/ARW/JPG}
    if [ ! -e "$jpgname" ];
    then
      echo "rm $f"
      rm "$f"
    fi
done