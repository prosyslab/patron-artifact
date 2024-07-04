#!/bin/sh
FILE_PATH=$(realpath "$0")
DIR_PATH=$(dirname "$FILE_PATH")
CIL_PATH="$DIR_PATH/cil"
OUT_PATH="$DIR_PATH/out"

# iterate over all out
for f in $OUT_PATH/*; do
  dir_name=$(basename $f)
  mkdir -p $CIL_PATH/$dir_name
  mkdir -p $CIL_PATH/$dir_name/bug
  mkdir -p $CIL_PATH/$dir_name/patch
  sparrow -il -frontend claml $f/bug.i > $CIL_PATH/$dir_name/bug/bug.c
  sparrow -il -frontend claml $f/patch.i > $CIL_PATH/$dir_name/patch/patch.c
done