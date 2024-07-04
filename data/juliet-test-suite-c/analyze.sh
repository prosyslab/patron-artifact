#!/bin/sh
FILE_PATH=$(realpath "$0")
DIR_PATH=$(dirname "$FILE_PATH")
CIL_PATH="$DIR_PATH/cilcopy"
OUT_PATH="$DIR_PATH/out"

# iterate over all out
for f in $CIL_PATH/*; do
  cd $f
  diff bug/bug.c patch/patch.c > diff
  # cd $f/bug
  # # sparrow $f/bug/bug.c -taint -extract_datalog_fact_full -unwrap_alloc -remove_cast -patron -tio -mio -pio -sio -bo -nd -dz &> /dev/nulls
  # if [ $(ls $f/bug/sparrow-out/taint/datalog | wc -l) -eq 0 ]; then
  #   rm -rf $f
  #   echo "Deleted $f"
  # fi

done